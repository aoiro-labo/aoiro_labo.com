// Minimal lightbox (~1.5KB): replaces GLightbox for article images
(function () {
  var overlay = null, imgEl = null, capEl = null, countEl = null;
  var items = [], index = 0, touchX = null;

  function eligible(img) {
    var a = img.closest('a');
    if (a) {
      var href = a.getAttribute('href') || '';
      if (/\.(jpe?g|png|webp|gif)([?#].*)?$/i.test(href)) return { src: href, cap: img.getAttribute('alt') || '' };
      return null; // image wrapped in a normal link: leave it alone
    }
    return { src: img.currentSrc || img.src, cap: img.getAttribute('alt') || '' };
  }

  function collect(clickedImg) {
    items = [];
    index = 0;
    var imgs = document.querySelectorAll('.prose img');
    Array.prototype.forEach.call(imgs, function (img) {
      var it = eligible(img);
      if (!it) return;
      if (img === clickedImg) index = items.length;
      items.push(it);
    });
  }

  function build() {
    overlay = document.createElement('div');
    overlay.className = 'mini-lb';
    overlay.innerHTML =
      '<button type="button" class="mini-lb-btn mini-lb-close" aria-label="閉じる">×</button>' +
      '<button type="button" class="mini-lb-btn mini-lb-prev" aria-label="前へ">‹</button>' +
      '<img alt="">' +
      '<button type="button" class="mini-lb-btn mini-lb-next" aria-label="次へ">›</button>' +
      '<div class="mini-lb-cap"></div>' +
      '<div class="mini-lb-count"></div>';
    document.body.appendChild(overlay);
    imgEl = overlay.querySelector('img');
    capEl = overlay.querySelector('.mini-lb-cap');
    countEl = overlay.querySelector('.mini-lb-count');
    overlay.addEventListener('click', function (e) { if (e.target === overlay) close(); });
    overlay.querySelector('.mini-lb-close').addEventListener('click', close);
    overlay.querySelector('.mini-lb-prev').addEventListener('click', function () { step(-1); });
    overlay.querySelector('.mini-lb-next').addEventListener('click', function () { step(1); });
    overlay.addEventListener('touchstart', function (e) { touchX = e.changedTouches[0].clientX; }, { passive: true });
    overlay.addEventListener('touchend', function (e) {
      if (touchX === null) return;
      var dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 40) step(dx < 0 ? 1 : -1);
      touchX = null;
    }, { passive: true });
    document.addEventListener('keydown', function (e) {
      if (!overlay.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowRight') step(1);
      if (e.key === 'ArrowLeft') step(-1);
    });
  }

  function show() {
    var it = items[index];
    if (!it) return;
    imgEl.src = it.src;
    capEl.textContent = it.cap;
    countEl.textContent = items.length > 1 ? (index + 1) + ' / ' + items.length : '';
    overlay.querySelector('.mini-lb-prev').style.display = items.length > 1 ? '' : 'none';
    overlay.querySelector('.mini-lb-next').style.display = items.length > 1 ? '' : 'none';
  }

  function step(d) {
    if (!items.length) return;
    index = (index + d + items.length) % items.length;
    show();
  }

  function open(img) {
    if (!overlay) build();
    collect(img);
    if (!items.length) return;
    show();
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function close() {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  document.addEventListener('click', function (e) {
    var img = e.target.closest && e.target.closest('.prose img');
    if (!img) return;
    if (!eligible(img)) return;
    e.preventDefault();
    open(img);
  });
})();
