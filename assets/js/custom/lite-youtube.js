// Lite YouTube embed: swap the thumbnail facade for the real iframe on demand.
(function () {
  function activate(el) {
    var id = el.getAttribute('data-yt-id');
    if (!id || el.classList.contains('active')) return;
    el.classList.add('active');
    var iframe = document.createElement('iframe');
    iframe.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
    iframe.title = el.getAttribute('aria-label') || 'YouTube動画';
    iframe.setAttribute('allow', 'accelerometer; autoplay; encrypted-media; picture-in-picture');
    iframe.setAttribute('allowfullscreen', '');
    el.innerHTML = '';
    el.appendChild(iframe);
  }
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('.lite-yt');
    if (el) activate(el);
  });
  document.addEventListener('keydown', function (e) {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.classList && e.target.classList.contains('lite-yt')) {
      e.preventDefault();
      activate(e.target);
    }
  });
})();
