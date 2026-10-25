const LinkFailure = (() => {
  async function run(e) {
    e.preventDefault();
    const [a, b] = $("#lfLink").value.split("|");
    const source = $("#lfSource").value, dest = $("#lfDest").value;
    const btn = e.submitter || $("#lfForm button");
    setBusy(btn, true, "Failing link…");
    try {
      const before = await Api.route(source, dest);
      const after = await Api.linkFailure(a, b, source, dest);
      const failed = [a, b];

      if (!after.new_path.length) {
        $("#lfSummary").innerHTML =
          `<div class="notice warn">Link ${esc(a)} ↔ ${esc(b)} failed and <b>${esc(dest)}</b> is now unreachable from <b>${esc(source)}</b>.</div>`;
        Graph.render($("#graphFailure"), App.topology, { oldPath: before.path, failed });
        return;
      }

      const delta = after.distance - before.distance;
      const affected = before.path.some((n, i) => i < before.path.length - 1 &&
        [n, before.path[i + 1]].sort().join() === [a, b].sort().join());

      $("#lfSummary").innerHTML = `
        <div class="notice ${affected ? "warn" : "ok"}">
          ${affected
            ? "The failed link was on the original route — traffic was rerouted."
            : "The failed link was not on the original route — no change needed."}
        </div>
        <div class="grid two">
          <div><h3>Original path <span class="pill">cost ${before.distance}</span></h3>${pathChips(before.path)}</div>
          <div><h3>New path <span class="pill">cost ${after.distance}</span></h3>${pathChips(after.new_path)}</div>
        </div>
        <p class="muted small">Cost change: <b>${delta > 0 ? "+" : ""}${delta}</b></p>`;
      Graph.render($("#graphFailure"), App.topology, {
        path: after.new_path,
        oldPath: affected ? before.path : [],
        failed
      });
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(btn, false);
    }
  }

  function init() {
    const nodes = App.topology.nodes.map(n => ({ value: n, label: n }));
    fillSelect($("#lfLink"), App.topology.links.map(l => ({ value: `${l.a}|${l.b}`, label: linkLabel(l) })), "StationB|StationC");
    fillSelect($("#lfSource"), nodes, "StationA");
    fillSelect($("#lfDest"), nodes, "Server");
    $("#lfForm").addEventListener("submit", run);
    Graph.render($("#graphFailure"), App.topology);
  }

  return { init };
})();
