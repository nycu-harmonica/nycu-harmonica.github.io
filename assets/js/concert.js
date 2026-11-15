// 竹夢初聲活動頁：標示下一場／已結束，並讓區塊在捲動時淡入。
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

  function revealOnScroll() {
    var targets = document.querySelectorAll(".concert-heading, .concert-show, .concert-set, .concert-outro__grid > *");
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
  revealOnScroll();
  setInterval(updateStatus, 60 * 1000);
  document.addEventListener("visibilitychange", function () {
    if (!document.hidden) updateStatus();
  });
})();
