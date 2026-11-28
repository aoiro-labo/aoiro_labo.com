// BudouX (Apache-2.0, Google) - phrase-based line breaking for Japanese.
// Applies to the page title and to headings/body text in articles.
import { HTMLProcessingParser } from '/js/budoux/html_processor.js';
import { model } from '/js/budoux/ja.js';

const parser = new HTMLProcessingParser(model);
const targets = document.querySelectorAll(
  'h1, article.prose h2, article.prose h3, article.prose h4,' +
  ' article.prose li, article.prose td, article.prose th,' +
  ' article.prose p:not(li p)'
);
targets.forEach((el) => {
  if (el.textContent.includes('\u200b')) return; // already baked at build time
  parser.applyToElement(el);
});
