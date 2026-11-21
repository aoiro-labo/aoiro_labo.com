(() => {
  // <stdin>
  (function() {
    function buildToggle() {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "toc-toggle";
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "\u6298\u308A\u305F\u305F\u307F\u3092\u5207\u308A\u66FF\u3048");
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 6 15 12 9 18"></polyline></svg>';
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
      items.forEach(function(li) {
        var childUl = li.querySelector(":scope > ul");
        if (!childUl) return;
        if (childUl.children.length < 2) return;
        var link = li.querySelector(":scope > a");
        if (!link) return;
        var toggle = buildToggle();
        link.classList.add("toc-item-has-toggle");
        link.parentNode.insertBefore(toggle, childUl);
        collapse(childUl, toggle);
        toggle.addEventListener("click", function(e) {
          e.preventDefault();
          e.stopPropagation();
          if (childUl.classList.contains("toc-collapsed")) {
            expand(childUl, toggle);
          } else {
            collapse(childUl, toggle);
          }
        });
        childUl.dataset.tocManaged = "true";
      });
      var observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(m) {
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
        subtree: true
      });
    }
    function init() {
      setupContainer("toc-content");
      setupContainer("toc-sidebar-content");
    }
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      setTimeout(init, 60);
    }
  })();
})();
