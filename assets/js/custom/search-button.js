// Add a search button to the top bar (opens the theme's search modal)
document.addEventListener('DOMContentLoaded', function () {
  var svg =
    '<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>';
  var cls =
    'border-border bg-background text-muted-foreground hover:text-primary hover:bg-primary/10 focus:ring-primary/20 flex h-10 w-10 items-center justify-center rounded-lg border transition-all duration-300 ease-out hover:scale-105 focus:ring-2 focus:outline-none active:scale-95 header-search-btn';
  document.querySelectorAll('header .space-x-2').forEach(function (box) {
    if (box.querySelector('.header-search-btn')) return;
    var b = document.createElement('button');
    b.type = 'button';
    b.className = cls;
    b.setAttribute('aria-label', 'サイト内検索');
    b.title = 'サイト内検索 (Ctrl+K)';
    b.innerHTML = svg;
    b.addEventListener('click', function () {
      if (window.Search) window.Search.show();
    });
    box.insertBefore(b, box.firstChild);
  });
});
