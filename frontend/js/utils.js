// Small DOM helpers shared by every page module.
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

function toast(message, type = "info") {
  const box = $("#toasts");
  const t = document.createElement("div");
  t.className = "toast " + type;
  t.textContent = message;
  box.appendChild(t);
  setTimeout(() => t.classList.add("show"), 10);
  setTimeout(() => {
    t.classList.remove("show");
    setTimeout(() => t.remove(), 300);
  }, 3500);
}

function setBusy(button, busy, label) {
  if (!button) return;
  if (busy) {
    button.dataset.label = button.textContent;
    button.disabled = true;
    if (label) button.textContent = label;
  } else {
    button.disabled = false;
    if (button.dataset.label) button.textContent = button.dataset.label;
  }
}

function fillSelect(select, options, selected) {
  select.innerHTML = "";
  options.forEach(o => {
    const opt = document.createElement("option");
    opt.value = o.value;
    opt.textContent = o.label;
    select.appendChild(opt);
  });
  if (selected !== undefined) select.value = selected;
}

function pathChips(path) {
  if (!path || !path.length) return '<span class="muted">No path</span>';
  return '<div class="chips">' + path.map((n, i) =>
    `<span class="chip node">${esc(n)}</span>` + (i < path.length - 1 ? '<span class="arrow">→</span>' : "")
  ).join("") + "</div>";
}

function pktChips(list, cls) {
  return '<div class="pkts">' + list.map(n => `<span class="pkt ${cls(n) || ""}">${n}</span>`).join("") + "</div>";
}

// Shared application state (filled by main.js once the topology is loaded).
const App = { topology: null };

const linkLabel = l => `${l.a} — ${l.b} (cost ${l.cost})`;
