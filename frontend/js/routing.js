const Routing = (() => {
  function tableRows(table) {
    return Object.entries(table).map(([dest, e]) => `
      <tr>
        <td>${esc(dest)}</td>
        <td>${e.next_hop ? esc(e.next_hop) : "—"}</td>
        <td>${e.cost === null ? "∞" : e.cost}</td>
        <td>${e.path && e.path.length ? esc(e.path.join(" → ")) : "—"}</td>
      </tr>`).join("");
  }

  async function run(e) {
    if (e) e.preventDefault();
    const source = $("#routeSource").value, dest = $("#routeDest").value;
    try {
      const r = await Api.route(source, dest);
      if (!r.path.length) {
        $("#routeSummary").innerHTML = '<div class="notice warn">No route exists between these nodes.</div>';
        Graph.render($("#graphRoute"), App.topology);
      } else {
        $("#routeSummary").innerHTML =
          `<div class="stats"><div class="stat"><span>${r.distance}</span><label>Total cost</label></div>` +
          `<div class="stat"><span>${r.path.length - 1}</span><label>Hops</label></div></div>` + pathChips(r.path);
        Graph.render($("#graphRoute"), App.topology, { path: r.path });
      }
      const t = await Api.routingTable(source);
      $("#routeTableNode").textContent = t.node;
      $("#routeTableMeta").textContent = `Converged in ${t.rounds_to_converge} round(s) of Distance Vector exchange.`;
      $("#routeTableBody").innerHTML = tableRows(t.table);
    } catch (err) {
      toast(err.message, "error");
    }
  }

  function init() {
    const nodes = App.topology.nodes.map(n => ({ value: n, label: n }));
    fillSelect($("#routeSource"), nodes, "Delhi");
    fillSelect($("#routeDest"), nodes, "Server");
    $("#routeForm").addEventListener("submit", run);
    run();
  }

  return { init, tableRows };
})();
