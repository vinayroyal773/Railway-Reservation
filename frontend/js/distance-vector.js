const DistanceVector = (() => {
  let result = null;

  function renderTables() {
    if (!result) return;
    const node = $("#dvNode").value;
    $("#dvBefore").innerHTML = Routing.tableRows(result.tables_before[node]);
    $("#dvAfter").innerHTML = Routing.tableRows(result.tables_after[node]);
  }

  async function run(e) {
    e.preventDefault();
    const failVal = $("#dvFail").value;
    const fail = failVal ? failVal.split("|") : null;
    const btn = e.submitter || $("#dvForm button");
    setBusy(btn, true, "Running…");
    try {
      result = await Api.distanceVector($("#dvPoison").checked, fail);

      $("#dvSummary").innerHTML = `
        <div class="stat"><span>${result.initial_rounds_to_converge}</span><label>Initial convergence rounds</label></div>
        <div class="stat ${fail ? "bad" : ""}"><span>${result.recovery_rounds_to_converge}</span><label>Recovery rounds</label></div>
        <div class="stat"><span>${result.poison_reverse ? "On" : "Off"}</span><label>Poison reverse</label></div>`;

      const hist = result.history_after_failure;
      $("#dvHistory").innerHTML = hist.length
        ? `<h3>Recovery after ${esc(result.failed_link.join(" ↔ "))} failed</h3>
           <div class="pkts">${hist.map(h =>
             `<span class="round ${h.changes ? "changed" : "stable"}" title="${h.changes} table entries changed">
                R${h.round}<small>${h.changes} Δ</small></span>`).join("")}</div>
           <p class="muted small">Each round shows how many routing-table entries changed; the network has converged when changes reach 0.</p>`
        : '<p class="muted small">No link failed — showing the initial converged tables.</p>';

      fillSelect($("#dvNode"), Object.keys(result.tables_before).map(n => ({ value: n, label: n })), "Delhi");
      $("#dvTablesCard").classList.remove("hidden");
      renderTables();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(btn, false);
    }
  }

  function init() {
    const opts = [{ value: "", label: "None" }].concat(
      App.topology.links.map(l => ({ value: `${l.a}|${l.b}`, label: linkLabel(l) })));
    fillSelect($("#dvFail"), opts, "Bhopal|Nagpur");
    $("#dvForm").addEventListener("submit", run);
    $("#dvNode").addEventListener("change", renderTables);
  }

  return { init };
})();
