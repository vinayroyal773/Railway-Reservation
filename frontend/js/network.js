const Network = (() => {
  function init() {
    Graph.render($("#graphNetwork"), App.topology);
    $("#linksBody").innerHTML = App.topology.links.map(l => `
      <tr>
        <td>${esc(l.a)} ↔ ${esc(l.b)}</td>
        <td>${l.cost}</td>
        <td>${l.delay_ms} ms</td>
        <td>${(l.loss * 100).toFixed(1)}%</td>
      </tr>`).join("");
  }
  return { init };
})();
