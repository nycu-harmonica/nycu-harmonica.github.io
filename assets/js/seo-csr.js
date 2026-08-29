// CSR SEO 狀態：canonical 固定為無 query 的靜態正式頁；只有具內容意義的
// Portal story/song 狀態會呼叫 setState 更新頁面標題、H1 與預覽文案。
(function () {
  'use strict';

  var canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) return;

  var canonicalURL;
  try {
    canonicalURL = new URL(canonical.href, window.location.origin);
    canonicalURL.search = '';
    canonicalURL.hash = '';
    canonical.href = canonicalURL.toString();
  } catch (_error) {
    return;
  }

  var heading = document.querySelector('[data-seo-heading]');
  var headingState = heading && heading.querySelector('[data-seo-heading-state]');
  var base = {
    title: document.title,
    description: (document.querySelector('meta[name="description"]') || {}).content || '',
    headingLabel: heading ? heading.textContent.trim() : '',
  };

  function cleanText(value, maxLength) {
    return String(value || '').replace(/\s+/g, ' ').trim().slice(0, maxLength);
  }

  function setMeta(selector, content) {
    var element = document.querySelector(selector);
    if (element) element.setAttribute('content', content);
  }

  function setState(state) {
    state = state || {};
    var stateTitle = cleanText(state.title, 90);
    var stateHeading = cleanText(state.heading || stateTitle, 120);
    var stateDescription = cleanText(state.description, 150);
    var title = stateTitle ? stateTitle + '｜' + base.title : base.title;
    var description = stateDescription || base.description;

    document.title = title;
    setMeta('meta[name="description"]', description);
    setMeta('meta[property="og:title"]', title);
    setMeta('meta[property="og:description"]', description);
    setMeta('meta[name="twitter:title"]', title);
    setMeta('meta[name="twitter:description"]', description);

    var previewURL = canonicalURL.toString();
    if (stateTitle) {
      try {
        var current = new URL(window.location.href);
        current.hash = '';
        previewURL = current.toString();
      } catch (_error) {}
    }
    setMeta('meta[property="og:url"]', previewURL);

    if (headingState) headingState.textContent = stateHeading ? '｜' + stateHeading : '';
    if (heading) heading.setAttribute('aria-label', stateHeading ? base.headingLabel + '｜' + stateHeading : base.headingLabel);
    document.documentElement.dataset.seoState = stateTitle ? 'query' : 'canonical';
  }

  window.BambooSEO = Object.freeze({
    canonicalURL: canonicalURL.toString(),
    setState: setState,
  });
  setState(null);
})();
