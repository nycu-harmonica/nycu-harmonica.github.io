(function () {
  'use strict';

  var configElement = document.getElementById('website-agent-config');
  var launch = document.getElementById('website-agent-launch');
  var dialog = document.getElementById('website-agent-dialog');
  var chat = document.getElementById('website-agent-chat');
  var loading = document.getElementById('website-agent-loading');
  var suggestions = document.getElementById('website-agent-suggestions');
  var sources = document.getElementById('website-agent-sources');
  var clear = document.getElementById('website-agent-clear');
  if (!configElement || !launch || !dialog || !chat || !loading || !sources) return;

  var config;
  try {
    config = JSON.parse(configElement.textContent || '{}');
  } catch (_error) {
    launch.hidden = true;
    return;
  }
  function endpointAllowed(value) {
    try {
      var url = new URL(value);
      if (url.protocol === 'https:') return true;
      var localPage = ['127.0.0.1', 'localhost'].indexOf(window.location.hostname) !== -1;
      var localEndpoint = ['127.0.0.1', 'localhost'].indexOf(url.hostname) !== -1;
      return localPage && localEndpoint && url.protocol === 'http:';
    } catch (_error) {
      return false;
    }
  }
  if (!endpointAllowed(config.endpoint || '') || !config.componentUrl) {
    launch.hidden = true;
    return;
  }

  var maxQuestionChars = Number(config.maxQuestionChars) || 500;
  var componentPromise;

  function setSources(items) {
    sources.replaceChildren();
    if (!Array.isArray(items) || !items.length) {
      sources.hidden = true;
      return;
    }
    var label = document.createElement('span');
    label.textContent = '相關公開資訊';
    sources.appendChild(label);
    items.forEach(function (source) {
      if (!source || !/^https:\/\//.test(source.url || '')) return;
      var link = document.createElement('a');
      link.href = source.url;
      link.textContent = source.label || '查看來源';
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      sources.appendChild(link);
    });
    sources.hidden = sources.childElementCount < 2;
  }

  function normaliseMessages(body) {
    var messages = body && Array.isArray(body.messages) ? body.messages : [];
    return messages.slice(-4).map(function (message) {
      return {
        role: message && message.role === 'ai' ? 'assistant' : 'user',
        text: String(message && message.text || '').replace(/\s+/g, ' ').trim().slice(0, maxQuestionChars)
      };
    }).filter(function (message) { return message.text; });
  }

  async function ask(body, signals) {
    var messages = normaliseMessages(body);
    var latest = messages[messages.length - 1];
    if (!latest || latest.role !== 'user') {
      await signals.onResponse({ error: '請輸入 1 到 500 個字的問題。' });
      return;
    }
    var controller = new AbortController();
    signals.stopClicked.listener = function () { controller.abort(); };
    var timeout = window.setTimeout(function () { controller.abort(); }, 60000);
    try {
      var response = await fetch(config.endpoint, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-store',
        credentials: 'omit',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: latest.text, history: messages.slice(0, -1) }),
        signal: controller.signal
      });
      var payload = await response.json().catch(function () { return {}; });
      if (!response.ok) {
        throw new Error(payload.message || '竹韻問答目前暫時無法使用。');
      }
      setSources(payload.sources);
      await signals.onResponse({ text: payload.answer || '目前沒有經確認的公開資訊。' });
    } catch (error) {
      var message = error && error.name === 'AbortError'
        ? '查詢時間較久，請稍後再試，或直接查看社團行事曆。'
        : (error.message || '竹韻問答目前暫時無法使用。');
      setSources([
        { label: '社團行事曆', url: 'https://harmonica.nycu.club/#calendar' },
        { label: 'Instagram', url: 'https://www.instagram.com/nycu_harmonica/' }
      ]);
      await signals.onResponse({ error: message });
    } finally {
      window.clearTimeout(timeout);
    }
  }

  function configureChat() {
    chat.connect = { handler: ask };
    chat.requestBodyLimits = { maxMessages: 4, totalMessagesMaxCharLength: 1800 };
    chat.chatStyle = { width: '100%', height: '100%', border: '0', borderRadius: '0', fontFamily: 'inherit' };
    chat.textInput = {
      characterLimit: maxQuestionChars,
      placeholder: { text: '輸入問題', style: { color: '#586c73' } },
      styles: {
        container: { border: '1px solid #c9dde2', borderRadius: '6px', boxShadow: 'none' },
        focus: { border: '1px solid #176b84', boxShadow: '0 0 0 2px #dceff3' }
      }
    };
    chat.submitButtonStyles = {
      submit: { container: { default: { backgroundColor: '#d59a32' }, hover: { backgroundColor: '#e1a73d' } } },
      loading: { container: { default: { backgroundColor: '#d59a32' } } },
      stop: { container: { default: { backgroundColor: '#176b84' } } },
      tooltip: { text: '送出問題' }
    };
    chat.messageStyles = {
      default: {
        shared: { bubble: { borderRadius: '6px', lineHeight: '1.65', overflowWrap: 'anywhere' } },
        user: { bubble: { backgroundColor: '#176b84', color: '#ffffff' } },
        ai: { bubble: { backgroundColor: '#ffffff', color: '#18343d', border: '1px solid #c9dde2' } }
      },
      error: { bubble: { backgroundColor: '#fff8eb', color: '#18343d', border: '1px solid #c67725' } }
    };
    chat.remarkable = { html: false, breaks: true, linkTarget: '_blank' };
    chat.introMessage = { text: '想知道怎麼加入、社課或最近活動嗎？我只會根據已核准的公開資料回答。' };
    chat.errorMessages = { displayServiceErrorMessages: true, overrides: { default: '竹韻問答目前暫時無法使用。' } };
    chat.images = false;
    chat.gifs = false;
    chat.camera = false;
    chat.audio = false;
    chat.microphone = false;
    chat.mixedFiles = false;
    chat.dragAndDrop = false;
    chat.speechToText = false;
    chat.textToSpeech = false;
    chat.hidden = false;
    loading.hidden = true;
  }

  function ensureComponent() {
    if (!componentPromise) {
      componentPromise = import(config.componentUrl).then(function () {
        return customElements.whenDefined('deep-chat');
      }).then(configureChat).catch(function () {
        loading.textContent = '問答介面目前無法載入，請稍後再試。';
        throw new Error('Deep Chat failed to load');
      });
    }
    return componentPromise;
  }

  launch.addEventListener('click', function () {
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
    ensureComponent().then(function () { chat.focusInput(); }).catch(function () {});
  });

  dialog.addEventListener('click', function (event) {
    if (event.target === dialog) dialog.close();
  });

  if (suggestions) {
    suggestions.addEventListener('click', function (event) {
      var button = event.target.closest('[data-agent-question]');
      if (!button) return;
      ensureComponent().then(function () {
        chat.submitUserMessage({ text: button.getAttribute('data-agent-question') || '' });
        suggestions.hidden = true;
      }).catch(function () {});
    });
  }

  if (clear) {
    clear.addEventListener('click', function () {
      if (typeof chat.clearMessages === 'function') chat.clearMessages();
      setSources([]);
      if (suggestions) suggestions.hidden = false;
      if (typeof chat.focusInput === 'function') chat.focusInput();
    });
  }
})();
