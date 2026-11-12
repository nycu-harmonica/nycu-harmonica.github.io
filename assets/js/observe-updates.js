// 即時載入觀測站竹韻來源 API；靜態 HTML 永遠保留為失敗時的備援。
(function (global) {
  'use strict';

  var API_URL = 'https://harmonica.observe.tw/api/source/198.json';
  var OBSERVE_ASSET_PREFIX = 'https://harmonica.observe.tw/assets/';
  var SOURCE_URL = 'https://harmonica.observe.tw/source/198-bamboo-melody-harmonica-club/';
  var SOURCE_ID = 198;
  var SOURCE_SLUG = 'bamboo-melody-harmonica-club';
  var SOURCE_NAME = '陽明交大竹韻口琴社';
  var MAX_ITEMS = 3;
  var MAX_TITLE_LENGTH = 140;
  var MAX_RESPONSE_BYTES = 1024 * 1024;
  var ITEM_ID_RE = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
  var PUNCTUATION = { ',': '，', ':': '：', ';': '；', '!': '！', '?': '？', '|': '｜', '~': '～' };
  var CJK_LEFT = /([\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff）】」』》〉])([,;:!?|~])/g;
  var CJK_RIGHT = /([,;:!?|~])([\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff（【「『《〈])/g;

  function normalizeDisplayText(value) {
    return String(value == null ? '' : value)
      .replace(/\s+/g, ' ')
      .trim()
      .replace(CJK_LEFT, function (_match, left, mark) { return left + PUNCTUATION[mark]; })
      .replace(CJK_RIGHT, function (_match, mark, right) { return PUNCTUATION[mark] + right; });
  }

  function compactText(value, maxLength, truncate) {
    var text = normalizeDisplayText(value);
    if (!text || /[<>]/.test(text)) return '';
    if (text.length <= maxLength) return text;
    if (!truncate) return '';
    return text.slice(0, maxLength - 1).trimEnd() + '…';
  }

  function validHttpsUrl(value) {
    try {
      var url = new URL(String(value || ''));
      if (url.protocol !== 'https:' || url.username || url.password || /\s/.test(String(value))) return '';
      return url.href;
    } catch (_error) {
      return '';
    }
  }

  function parseTimestamp(value, label) {
    if (typeof value !== 'string' || !/[T]/.test(value)) throw new Error(label + ' 格式錯誤');
    var date = new Date(value);
    if (Number.isNaN(date.getTime())) throw new Error(label + ' 格式錯誤');
    return date;
  }

  function formatTaipei(value) {
    var date = value instanceof Date ? value : parseTimestamp(value, 'timestamp');
    var parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Taipei',
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', hourCycle: 'h23'
    }).formatToParts(date);
    var values = {};
    parts.forEach(function (part) { values[part.type] = part.value; });
    return values.year + '/' + values.month + '/' + values.day + ' ' + values.hour + ':' + values.minute;
  }

  function utf8ByteLength(value) {
    var text = String(value);
    if (typeof global.TextEncoder === 'function') return new global.TextEncoder().encode(text).byteLength;
    var bytes = 0;
    for (var index = 0; index < text.length; index += 1) {
      var code = text.charCodeAt(index);
      if (code <= 0x7f) bytes += 1;
      else if (code <= 0x7ff) bytes += 2;
      else if (code >= 0xd800 && code <= 0xdbff && index + 1 < text.length &&
               text.charCodeAt(index + 1) >= 0xdc00 && text.charCodeAt(index + 1) <= 0xdfff) {
        bytes += 4;
        index += 1;
      } else bytes += 3;
    }
    return bytes;
  }

  function validateSource(source) {
    if (!source || typeof source !== 'object' ||
        source.id !== SOURCE_ID || source.slug !== SOURCE_SLUG ||
        source.name !== SOURCE_NAME || source.pageUrl !== SOURCE_URL) {
      throw new Error('來源 metadata 不符合竹韻來源');
    }
    return { id: SOURCE_ID, slug: SOURCE_SLUG, name: SOURCE_NAME, pageUrl: SOURCE_URL };
  }

  // 只接受觀測站自己快取的圖片;平台原始 CDN 網址會過期,也會把訪客請求送去第三方。
  function normalizeImage(value) {
    if (!value || typeof value !== 'object') return null;
    var url = validHttpsUrl(value.url);
    if (!url || url.indexOf(OBSERVE_ASSET_PREFIX) !== 0) return null;
    var width = Number(value.width);
    var height = Number(value.height);
    var image = { url: url };
    if (Number.isInteger(width) && width > 0 && Number.isInteger(height) && height > 0) {
      image.width = width;
      image.height = height;
    }
    return image;
  }

  function normalizeItem(row) {
    if (!row || typeof row !== 'object' || row.sourceName !== SOURCE_NAME) return null;
    var id = String(row.id || '').trim();
    var title = compactText(row.title, MAX_TITLE_LENGTH, true);
    var source = compactText(row.sourceName, 80, false);
    var platform = compactText(row.platform, 40, false);
    var url = validHttpsUrl(row.url);
    var published;
    try { published = parseTimestamp(row.publishedAt, 'publishedAt'); } catch (_error) { return null; }
    if (!ITEM_ID_RE.test(id) || !title || !source || !platform || !url) return null;
    return {
      id: id,
      title: title,
      url: url,
      sourceName: source,
      platform: platform,
      image: normalizeImage(row.image),
      publishedAt: row.publishedAt,
      postedAtLocal: formatTaipei(published)
    };
  }

  function normalizePayload(payload) {
    if (!payload || typeof payload !== 'object' || payload.schemaVersion !== 1) {
      throw new Error('API schemaVersion 不是 1');
    }
    var source = validateSource(payload.source);
    parseTimestamp(payload.generatedAt, 'generatedAt');
    if (!Array.isArray(payload.items)) throw new Error('API 缺少 items');
    var items = [];
    var seenIds = new Set();
    var seenUrls = new Set();
    payload.items.some(function (row) {
      var item = normalizeItem(row);
      if (!item || seenIds.has(item.id) || seenUrls.has(item.url)) return false;
      items.push(item);
      seenIds.add(item.id);
      seenUrls.add(item.url);
      return items.length === MAX_ITEMS;
    });
    if (!items.length) {
      var empty = new Error('API 沒有安全的竹韻動態');
      empty.reason = payload.items.length ? 'invalid' : 'empty';
      throw empty;
    }
    return { generatedAt: payload.generatedAt, source: source, items: items };
  }

  function createUpdateCard(doc, item) {
    var article = doc.createElement('article');
    article.className = 'card observe-update-card';
    if (item.image) {
      var figure = doc.createElement('a');
      figure.className = 'observe-update-media';
      figure.setAttribute('href', item.url);
      figure.setAttribute('target', '_blank');
      figure.setAttribute('rel', 'noopener noreferrer');
      figure.setAttribute('tabindex', '-1');
      figure.setAttribute('aria-hidden', 'true');
      var picture = doc.createElement('img');
      picture.setAttribute('src', item.image.url);
      picture.setAttribute('alt', '');
      picture.setAttribute('loading', 'lazy');
      picture.setAttribute('decoding', 'async');
      picture.setAttribute('referrerpolicy', 'no-referrer');
      if (item.image.width) {
        picture.setAttribute('width', String(item.image.width));
        picture.setAttribute('height', String(item.image.height));
      }
      figure.append(picture);
      article.append(figure);
    }
    var body = doc.createElement('div');
    body.className = 'card-body';
    var dateLine = doc.createElement('p');
    dateLine.className = 'card-date';
    var time = doc.createElement('time');
    time.setAttribute('datetime', item.publishedAt);
    time.textContent = item.postedAtLocal;
    var platform = doc.createElement('span');
    platform.className = 'card-platform';
    platform.textContent = item.platform;
    dateLine.append(time, platform);
    var heading = doc.createElement('h3');
    heading.className = 'card-title';
    var link = doc.createElement('a');
    link.setAttribute('href', item.url);
    link.setAttribute('target', '_blank');
    link.setAttribute('rel', 'noopener noreferrer');
    link.textContent = item.title;
    heading.append(link);
    body.append(dateLine, heading);
    article.append(body);
    return article;
  }

  function renderUpdates(doc, grid, status, normalized) {
    var cards = normalized.items.map(function (item) { return createUpdateCard(doc, item); });
    grid.replaceChildren.apply(grid, cards);
    grid.dataset.observeMode = 'live';
    setStatus(status, 'live', '已讀取最新動態（' + formatTaipei(normalized.generatedAt) + ' 更新）・' + SOURCE_NOTE);
  }

  var SOURCE_NOTE = '資料來自臺灣口琴觀測站，內容以原始貼文為準';

  // 狀態列分成 loading / live / fallback 三種；訪客永遠看得到目前畫面是哪一份資料。
  function setStatus(status, mode, text) {
    status.dataset.observeMode = mode;
    var target = typeof status.querySelector === 'function' ? status.querySelector('[data-status-text]') : null;
    (target || status).textContent = text;
  }

  function fallbackText(status, reason) {
    var time = status.dataset && status.dataset.fallbackTime;
    var shown = time ? '先顯示 ' + time + ' 同步的動態' : '先顯示網站內建的動態';
    if (reason === 'empty') return '觀測站目前沒有新的公開貼文，' + shown;
    return '暫時連不上臺灣口琴觀測站，' + shown;
  }

  async function refreshObserveUpdates(options) {
    options = options || {};
    var doc = options.document || global.document;
    if (!doc) return false;
    var grid = options.grid || doc.getElementById('observe-updates-grid');
    var status = options.status || doc.getElementById('observe-updates-status');
    if (!grid || !status) return false;
    var fetchImpl = options.fetchImpl || global.fetch;
    var AbortControllerImpl = options.AbortControllerImpl || global.AbortController;
    if (typeof fetchImpl !== 'function' || typeof AbortControllerImpl !== 'function') return false;
    var setTimer = options.setTimeoutImpl || global.setTimeout;
    var clearTimer = options.clearTimeoutImpl || global.clearTimeout;
    var controller = new AbortControllerImpl();
    var timer = setTimer(function () { controller.abort(); }, options.timeoutMs || 8000);
    setStatus(status, 'loading', '正在讀取觀測站的最新動態…');
    try {
      var response = await fetchImpl(API_URL, {
        method: 'GET', mode: 'cors', credentials: 'omit', cache: 'no-cache',
        headers: { Accept: 'application/json' }, signal: controller.signal
      });
      if (!response.ok) throw new Error('API HTTP ' + response.status);
      var length = Number(response.headers && response.headers.get && response.headers.get('content-length'));
      if (Number.isFinite(length) && length > MAX_RESPONSE_BYTES) throw new Error('API 回應過大');
      var raw = await response.text();
      if (utf8ByteLength(raw) > MAX_RESPONSE_BYTES) throw new Error('API 回應過大');
      var normalized = normalizePayload(JSON.parse(raw));
      renderUpdates(doc, grid, status, normalized);
      return true;
    } catch (error) {
      grid.dataset.observeMode = 'fallback';
      setStatus(status, 'fallback', fallbackText(status, error && error.reason));
      return false;
    } finally {
      clearTimer(timer);
    }
  }

  var api = {
    normalizeDisplayText: normalizeDisplayText,
    normalizePayload: normalizePayload,
    renderUpdates: renderUpdates,
    refreshObserveUpdates: refreshObserveUpdates
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  global.ObserveUpdates = api;
  if (global.document) {
    var start = function () { refreshObserveUpdates(); };
    if (global.document.readyState === 'loading') global.document.addEventListener('DOMContentLoaded', start);
    else start();
  }
})(typeof window !== 'undefined' ? window : globalThis);
