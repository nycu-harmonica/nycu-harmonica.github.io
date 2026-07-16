// 手機選單 + 相簿 lightbox(無相依套件)
(function () {
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
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
