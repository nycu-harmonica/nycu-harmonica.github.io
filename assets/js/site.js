// 手機選單 + 相簿 lightbox(無相依套件)
(function () {
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    var desktopMedia = window.matchMedia('(min-width: 768px)');

    function setNavOpen(open, returnFocus) {
      nav.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? '關閉選單' : '開啟選單');
      if (returnFocus) toggle.focus();
    }

    toggle.addEventListener('click', function () {
      setNavOpen(!nav.classList.contains('open'), false);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !desktopMedia.matches && nav.classList.contains('open')) {
        setNavOpen(false, true);
      }
    });

    function resetNavOnDesktop(event) {
      if (event.matches) setNavOpen(false, false);
    }

    desktopMedia.addEventListener('change', resetNavOnDesktop);
  }

  // Google 日曆嵌入：進入畫面 4.5 秒後還沒畫好，就把後方的說明換成「載不出來」與替代資訊。
  // 跨網域 iframe 無法得知內容是否成功，所以說明放在 iframe 下層，日曆畫好時自然被蓋住。
  document.querySelectorAll('[data-calendar-embed]').forEach(function (embed) {
    var frame = embed.querySelector('iframe');
    if (!frame) return;
    function arm() {
      window.setTimeout(function () { embed.classList.add('is-slow'); }, 4500);
    }
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        if (entries.some(function (entry) { return entry.isIntersecting; })) {
          observer.disconnect();
          arm();
        }
      });
      observer.observe(embed);
    } else arm();
  });

  // 「詢問竹韻」浮動鈕在頁尾出現時讓位（頁尾本身就有聯絡方式）。
  var launch = document.getElementById('website-agent-launch');
  var footer = document.querySelector('.site-footer');
  if (launch && footer && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      launch.classList.toggle('is-docked', entries[0].isIntersecting);
    }, { rootMargin: '0px 0px -40px 0px' }).observe(footer);
  }
  // 手機往下讀的時候先收起來，往回捲才出現，避免一直蓋住標題與內文。
  if (launch) {
    var lastY = window.scrollY;
    var narrow = window.matchMedia('(max-width: 639px)');
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      if (narrow.matches) launch.classList.toggle('is-tucked', y > lastY && y > 240);
      else launch.classList.remove('is-tucked');
      lastY = y;
    }, { passive: true });
  }

  // 限時區塊:過期(data-expires)就隱藏,不必等網站重新建置
  document.querySelectorAll('[data-expires]').forEach(function (el) {
    var expires = Date.parse(el.dataset.expires || '');
    if (expires && Date.now() >= expires) el.hidden = true;
  });

  // 臨時公告 popup:過期就不顯示。重整或從站外進來都會再跳;
  // 只有「這次瀏覽已點掉 + 站內連結換頁」才不重複打擾。
  var announce = document.getElementById('announcement');
  if (announce && typeof announce.showModal === 'function') {
    var announceKey = 'announcement-dismissed:' + (announce.dataset.id || '');
    var announceExpires = Date.parse(announce.dataset.expires || '');
    var announceDismissed = false;
    try { announceDismissed = sessionStorage.getItem(announceKey) === '1'; } catch (e) {}
    var navEntry = (performance.getEntriesByType && performance.getEntriesByType('navigation')[0]) || null;
    var internalNav = navEntry && (navEntry.type === 'back_forward' ||
      (navEntry.type === 'navigate' && document.referrer.indexOf(location.origin + '/') === 0));
    if (!(announceDismissed && internalNav) && !(announceExpires && Date.now() >= announceExpires)) {
      announce.showModal();
    }
    announce.addEventListener('close', function () {
      try { sessionStorage.setItem(announceKey, '1'); } catch (e) {}
    });
    announce.addEventListener('click', function (e) {
      if (e.target === announce) announce.close();
    });
    var announceClose = document.getElementById('announcement-close');
    if (announceClose) announceClose.addEventListener('click', function () { announce.close(); });
  }

  var box = document.getElementById('lightbox');
  var img = document.getElementById('lightbox-img');
  if (box && img) {
    document.querySelectorAll('.js-lightbox').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        img.src = a.dataset.full || a.href;
        img.alt = a.getAttribute('aria-label') || '放大照片';
        box.showModal();
      });
    });
    box.addEventListener('click', function (e) {
      if (e.target === box) box.close();
    });
    var close = document.getElementById('lightbox-close');
    if (close) close.addEventListener('click', function () { box.close(); });
    box.addEventListener('close', function () {
      img.src = '';
      img.alt = '';
    });
  }
})();
