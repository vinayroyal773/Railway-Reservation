// Renders the network topology as an SVG diagram.
const Graph = (() => {
  const NS = "http://www.w3.org/2000/svg";
  const W = 680, H = 320;

  // Hand-tuned layout for the default topology; unknown nodes fall back to a circle.
  const FIXED = {
    Delhi: [70, 160], Bhopal: [230, 65], Mumbai: [230, 255],
    Nagpur: [450, 65], Hyderabad: [450, 255], Server: [610, 160]
  };

  function layout(nodes) {
    const pos = {};
    nodes.forEach((n, i) => {
      if (FIXED[n]) { pos[n] = FIXED[n]; return; }
      const a = (2 * Math.PI * i) / nodes.length;
      pos[n] = [W / 2 + 240 * Math.cos(a), H / 2 + 110 * Math.sin(a)];
    });
    return pos;
  }

  const key = (a, b) => [a, b].sort().join("|");
  const make = (tag, attrs = {}) => {
    const e = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
    return e;
  };

  function pathEdges(path) {
    const s = new Set();
    for (let i = 0; i < (path || []).length - 1; i++) s.add(key(path[i], path[i + 1]));
    return s;
  }

  /**
   * render(container, topology, { path, oldPath, failed })
   *   path    - nodes of the highlighted (green) route
   *   oldPath - nodes of a secondary (amber) route
   *   failed  - [a, b] link drawn as broken (red, dashed)
   */
  function render(container, topology, opts = {}) {
    const { path = [], oldPath = [], failed = null } = opts;
    const pos = layout(topology.nodes);
    const main = pathEdges(path), old = pathEdges(oldPath);
    const failedKey = failed ? key(failed[0], failed[1]) : null;
    const onPath = new Set(path);

    const svg = make("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Network topology" });

    topology.links.forEach(l => {
      const [x1, y1] = pos[l.a], [x2, y2] = pos[l.b];
      const k = key(l.a, l.b);
      let cls = "edge";
      if (k === failedKey) cls += " failed";
      else if (main.has(k)) cls += " path";
      else if (old.has(k)) cls += " old";
      const g = make("g");
      const line = make("line", { x1, y1, x2, y2, class: cls });
      const title = make("title");
      title.textContent = `${l.a} ↔ ${l.b} · cost ${l.cost} · ${l.delay_ms} ms · loss ${(l.loss * 100).toFixed(0)}%`;
      line.appendChild(title);
      g.appendChild(line);

      const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
      g.appendChild(make("circle", { cx: mx, cy: my, r: 11, class: "cost-bg" }));
      const t = make("text", { x: mx, y: my + 4, class: "cost-text", "text-anchor": "middle" });
      t.textContent = l.cost;
      g.appendChild(t);
      svg.appendChild(g);
    });

    topology.nodes.forEach(n => {
      const [x, y] = pos[n];
      const isServer = n === "Server";
      const g = make("g", { class: "node" + (isServer ? " server" : "") + (onPath.has(n) ? " on-path" : "") });
      if (isServer) g.appendChild(make("rect", { x: x - 34, y: y - 22, width: 68, height: 44, rx: 8 }));
      else g.appendChild(make("circle", { cx: x, cy: y, r: 32 }));
      const label = make("text", { x, y: y + 4, "text-anchor": "middle", "font-size": isServer ? 14 : 11 });
      label.textContent = isServer ? "Server" : n;
      g.appendChild(label);
      svg.appendChild(g);
    });

    container.innerHTML = "";
    container.appendChild(svg);
  }

  return { render };
})();
