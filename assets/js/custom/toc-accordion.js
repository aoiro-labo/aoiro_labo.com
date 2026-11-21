// TOC accordion: collapse heading groups that have more than one sub-item,
// and keep the active section auto-expanded as Gumshoe highlights it.
(function () {
  function buildToggle() {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "toc-toggle";
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-label", "折りたたみを切り替え");
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 6 15 12 9 18"></polyline></svg>';
    return btn;
  }

  function expand(ul, toggle) {
    ul.classList.remove("toc-collapsed");
    ul.style.maxHeight = ul.scrollHeight + "px";
    if (toggle) toggle.setAttribute("aria-expanded", "true");
  }

  function collapse(ul, toggle) {
    ul.classList.add("toc-collapsed");
    ul.style.maxHeight = "0px";
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }

  function setupContainer(containerId) {
    var container = document.getElementById(containerId);
    if (!container) return;

    var items = container.querySelectorAll("li");
    items.forEach(function (li) {
      var childUl = li.querySelector(":scope > ul");
      if (!childUl) return;
      // Only bother collapsing groups with real bulk (2+ sub-items).
      if (childUl.children.length < 2) return;

      var link = li.querySelector(":scope > a");
      if (!link) return;

      var toggle = buildToggle();
      link.classList.add("toc-item-has-toggle");
      link.parentNode.insertBefore(toggle, childUl);

      collapse(childUl, toggle);

      toggle.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (childUl.classList.contains("toc-collapsed")) {
          expand(childUl, toggle);
        } else {
          collapse(childUl, toggle);
        }
      });

      // Keep the growable region correctly sized if fonts/layout shift.
      childUl.dataset.tocManaged = "true";
    });

    // Auto-expand ancestors of whatever Gumshoe marks active so the
    // reader's current position is never hidden inside a collapsed group.
    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        if (m.type !== "attributes" || m.attributeName !== "class") return;
        var el = m.target;
        if (!(el instanceof Element)) return;
        if (!el.classList.contains("active") && !el.classList.contains("active-parent")) return;

        var node = el;
        while (node && node !== container) {
          if (node.tagName === "UL" && node.classList.contains("toc-collapsed")) {
            var parentLi = node.parentElement;
            var toggle = parentLi ? parentLi.querySelector(":scope > .toc-toggle") : null;
            expand(node, toggle);
          }
          node = node.parentElement;
        }
      });
    });

    observer.observe(container, {
      attributes: true,
      attributeFilter: ["class"],
      subtree: true,
    });
  }

  function init() {
    setupContainer("toc-content");
    setupContainer("toc-sidebar-content");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    // Run after the theme's own toc.js has had a chance to render/attach.
    setTimeout(init, 60);
  }
})();
