// Copy button for code blocks in articles
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.prose pre').forEach(function (pre) {
    if (pre.classList.contains('mermaid')) return;
    var host = pre.closest('.highlight') || pre;
    host.classList.add('code-host');
    if (host.querySelector('.code-copy-btn')) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'code-copy-btn';
    btn.textContent = 'コピー';
    btn.setAttribute('aria-label', 'コードをコピー');
    btn.addEventListener('click', function () {
      var code = pre.querySelector('code');
      var text = code ? code.innerText : pre.innerText;
      function done() {
        btn.textContent = 'コピーしました';
        setTimeout(function () { btn.textContent = 'コピー'; }, 1500);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done).catch(function () { fallback(); done(); });
      } else { fallback(); done(); }
      function fallback() {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (e) {}
        ta.remove();
      }
    });
    host.appendChild(btn);
  });
});
