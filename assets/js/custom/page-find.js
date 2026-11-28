// Dock search = in-page find (top bar search stays site-wide)
(function () {
  var marks = [];
  var current = -1;
  var bar = null;
  var input = null;
  var countEl = null;

  function buildBar() {
    bar = document.createElement('div');
    bar.className = 'page-find-bar';
    bar.innerHTML =
      '<input type="text" placeholder="ページ内検索" aria-label="ページ内検索">' +
      '<span class="page-find-count"></span>' +
      '<button type="button" class="page-find-prev" aria-label="前へ">↑</button>' +
      '<button type="button" class="page-find-next" aria-label="次へ">↓</button>' +
      '<button type="button" class="page-find-close" aria-label="閉じる">×</button>';
    document.body.appendChild(bar);
    input = bar.querySelector('input');
    countEl = bar.querySelector('.page-find-count');
    bar.querySelector('.page-find-next').addEventListener('click', function () { step(1); });
    bar.querySelector('.page-find-prev').addEventListener('click', function () { step(-1); });
    bar.querySelector('.page-find-close').addEventListener('click', closeBar);
    input.addEventListener('input', function () { run(input.value); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); step(e.shiftKey ? -1 : 1); }
      if (e.key === 'Escape') closeBar();
    });
  }

  function clearMarks() {
    marks.forEach(function (m) {
      var p = m.parentNode;
      if (p) { p.replaceChild(document.createTextNode(m.textContent), m); p.normalize(); }
    });
    marks = [];
    current = -1;
  }

  function scopeRoot() {
    return document.querySelector('main') || document.body;
  }

  function run(q) {
    clearMarks();
    countEl.textContent = '';
    q = (q || '').trim();
    if (!q) return;
    var root = scopeRoot();
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue || node.nodeValue.toLowerCase().indexOf(q.toLowerCase()) === -1)
          return NodeFilter.FILTER_REJECT;
        var p = node.parentElement;
        if (!p || p.closest('.page-find-bar, #dock, script, style, noscript')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    var lower = q.toLowerCase();
    nodes.forEach(function (node) {
      var text = node.nodeValue;
      var frag = document.createDocumentFragment();
      var idx = 0;
      var hay = text.toLowerCase();
      var pos;
      while ((pos = hay.indexOf(lower, idx)) !== -1) {
        frag.appendChild(document.createTextNode(text.slice(idx, pos)));
        var mark = document.createElement('mark');
        mark.className = 'page-find-hit';
        mark.textContent = text.slice(pos, pos + q.length);
        frag.appendChild(mark);
        marks.push(mark);
        idx = pos + q.length;
      }
      frag.appendChild(document.createTextNode(text.slice(idx)));
      node.parentNode.replaceChild(frag, node);
    });
    if (marks.length) {
      current = 0;
      showCurrent();
    }
    countEl.textContent = marks.length ? '0/' + marks.length : '0件';
    if (marks.length) updateCount();
  }

  function updateCount() {
    countEl.textContent = marks.length ? (current + 1) + '/' + marks.length : '0件';
  }

  function showCurrent() {
    marks.forEach(function (m, i) { m.classList.toggle('page-find-current', i === current); });
    if (marks[current]) marks[current].scrollIntoView({ block: 'center', behavior: 'smooth' });
    updateCount();
  }

  function step(d) {
    if (!marks.length) { run(input.value); return; }
    current = (current + d + marks.length) % marks.length;
    showCurrent();
  }

  function openBar() {
    if (!bar) buildBar();
    bar.classList.add('open');
    input.focus();
    input.select();
  }

  function closeBar() {
    if (!bar) return;
    bar.classList.remove('open');
    clearMarks();
    countEl.textContent = '';
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('dock-search');
    if (btn) {
      btn.title = 'ページ内検索';
      btn.setAttribute('aria-label', 'ページ内検索');
      var label = btn.querySelector('span');
      if (label) label.textContent = 'ページ内';
    }
  });

  // Capture phase: intercept before dock.js opens the site search modal
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('#dock-search');
    if (t) {
      e.preventDefault();
      e.stopPropagation();
      openBar();
    }
  }, true);
})();
