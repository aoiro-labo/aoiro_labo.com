// Sync giscus theme with the site theme (params keep preferred_color_scheme as the initial value)
(function () {
  function currentTheme() {
    var el = document.documentElement;
    if (el.classList.contains('dark') || el.getAttribute('data-theme') === 'dark') return 'dark';
    if (el.classList.contains('light') || el.getAttribute('data-theme') === 'light') return 'light';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function sync() {
    var frame = document.querySelector('iframe.giscus-frame');
    if (!frame || !frame.contentWindow) return;
    frame.contentWindow.postMessage(
      { giscus: { setConfig: { theme: currentTheme() } } },
      'https://giscus.app'
    );
  }
  var tries = 0;
  var timer = setInterval(function () {
    if (document.querySelector('iframe.giscus-frame')) { sync(); clearInterval(timer); }
    if (++tries > 40) clearInterval(timer);
  }, 500);
  new MutationObserver(sync).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class', 'data-theme'],
  });
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', sync);
})();
