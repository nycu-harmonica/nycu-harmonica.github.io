// 竹夢初聲活動頁：標示下一場／已結束、場次分頁、複製 hashtag，並讓區塊在捲動時淡入。
// 沒有 JavaScript 時頁面內容完整可讀，這裡只做加強。
(function () {
  "use strict";

  var DAY = 24 * 60 * 60 * 1000;
  var TAIPEI_OFFSET = 8 * 60 * 60 * 1000;

  // 以臺灣日曆日計算相差天數，避免訪客裝置時區造成「還有 N 天」差一天。
  function taipeiDay(ms) {
    return Math.floor((ms + TAIPEI_OFFSET) / DAY);
  }

  function updateStatus() {
    var now = Date.now();
    var nextMarked = false;
    var shows = document.querySelectorAll(".concert-show");
    Array.prototype.forEach.call(shows, function (show) {
      var start = Date.parse(show.getAttribute("data-start"));
      var end = Date.parse(show.getAttribute("data-end"));
      var badge = show.querySelector(".concert-show__status");
      if (!badge || isNaN(start) || isNaN(end)) return;

      show.classList.remove("is-past", "is-next", "is-live");
      var text = "";
      if (now >= end) {
        show.classList.add("is-past");
        text = "已結束";
      } else if (now >= start) {
        show.classList.add("is-live");
        nextMarked = true;
        text = "演出中";
      } else if (!nextMarked) {
        nextMarked = true;
        show.classList.add("is-next");
        var days = taipeiDay(start) - taipeiDay(now);
        text = "下一場・" + (days <= 0 ? "就是今天" : days === 1 ? "明天" : "還有 " + days + " 天");
      }
      badge.textContent = text;
      badge.hidden = !text;
    });
  }

  // 場次分頁：一次顯示一場，預設打開下一場（或演出中的那場）。網址帶 #show-xxx 時打開那一場。
  function setupTabs() {
    var tabs = Array.prototype.slice.call(document.querySelectorAll(".concert-tab"));
    if (!tabs.length) return;
    function panelOf(tab) { return document.getElementById(tab.getAttribute("aria-controls")); }
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        if (on) panelOf(t).removeAttribute("data-inactive");
        else panelOf(t).setAttribute("data-inactive", "");
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function (event) {
        event.preventDefault();
        select(tab);
        if (history.replaceState) history.replaceState(null, "", tab.getAttribute("href"));
      });
      tab.addEventListener("keydown", function (event) {
        var step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (!step) return;
        event.preventDefault();
        select(tabs[(i + step + tabs.length) % tabs.length], true);
      });
    });
    document.documentElement.classList.add("concert-tabs-ready");
    var fromHash = tabs.filter(function (t) { return t.getAttribute("href") === location.hash; })[0];
    var upcoming = tabs.filter(function (t) {
      var show = panelOf(t).querySelector(".concert-show");
      return show && (show.classList.contains("is-next") || show.classList.contains("is-live"));
    })[0];
    select(fromHash || upcoming || tabs[0]);
  }

  // 「我們現場見」的 hashtag：點一下複製。
  function setupCopy() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-copy]"), function (button) {
      var label = button.querySelector("[data-copy-label]");
      if (!navigator.clipboard || !label) return;
      var original = label.textContent;
      label.hidden = false;
      button.addEventListener("click", function () {
        navigator.clipboard.writeText(button.getAttribute("data-copy")).then(function () {
          label.textContent = "已複製，發文時貼上";
          button.classList.add("is-copied");
          setTimeout(function () { label.textContent = original; button.classList.remove("is-copied"); }, 2400);
        });
      });
    });
  }

  function revealOnScroll() {
    var targets = document.querySelectorAll(".concert-heading, .concert-tabs, .concert-panel, .concert-outro__grid > *");
    var query = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
    if ((query && query.matches) || !("IntersectionObserver" in window)) return;
    document.documentElement.classList.add("concert-motion");
    // 訪客中途開啟「減少動態效果」時，立刻顯示所有內容。
    if (query && query.addEventListener) {
      query.addEventListener("change", function (event) {
        if (event.matches) document.documentElement.classList.remove("concert-motion");
      });
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    Array.prototype.forEach.call(targets, function (el) { observer.observe(el); });
  }

  updateStatus();
  setupTabs();
  setupCopy();
  revealOnScroll();
  setInterval(updateStatus, 60 * 1000);
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) updateStatus();
  });
})();
