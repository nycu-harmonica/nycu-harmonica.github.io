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
