const Reservations = (() => {
  let rows = [];

  function today() {
    const d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 10);
  }

  async function load() {
    try {
      rows = await Api.listReservations();
      render();
    } catch (e) {
      toast(e.message, "error");
    }
  }

  function render() {
    const q = $("#resSearch").value.trim().toLowerCase();
    const status = $("#resFilter").value;
    const shown = rows.filter(r =>
      (status === "ALL" || r.status === status) &&
      (!q || [r.name, r.pnr, r.source, r.destination].some(v => String(v).toLowerCase().includes(q)))
    );

    $("#statTotal").textContent = rows.length;
    $("#statConfirmed").textContent = rows.filter(r => r.status === "CONFIRMED").length;
    $("#statCancelled").textContent = rows.filter(r => r.status === "CANCELLED").length;

    $("#resBody").innerHTML = shown.map(r => `
      <tr>
        <td title="Booking #${r.id}"><code>${esc(r.pnr)}</code></td>
        <td>${esc(r.name)}</td>
        <td>${esc(r.source)}</td>
        <td>${esc(r.destination)}</td>
        <td>${esc(r.date)}</td>
        <td><span class="badge ${r.status === "CONFIRMED" ? "ok" : "bad"}">${esc(r.status)}</span></td>
        <td class="right">${r.status === "CONFIRMED"
          ? `<button class="btn small danger" data-cancel="${r.id}">Cancel</button>` : ""}</td>
      </tr>`).join("");
    $("#resEmpty").classList.toggle("hidden", shown.length > 0);
  }

  async function previewRoute() {
    const s = $("#resSource").value, d = $("#resDest").value;
    const box = $("#routePreview");
    if (!s || !d) return;
    if (s === d) {
      box.innerHTML = "Source and destination must differ.";
      box.className = "route-preview warn";
      return;
    }
    try {
      const r = await Api.route(s, d);
      if (!r.path.length) {
        box.innerHTML = "No route available between these stations.";
        box.className = "route-preview warn";
      } else {
        box.innerHTML = `<b>Route (cost ${r.distance}):</b> ` + pathChips(r.path);
        box.className = "route-preview";
      }
    } catch (e) {
      box.textContent = e.message;
      box.className = "route-preview warn";
    }
  }

  async function submit(e) {
    e.preventDefault();
    const data = {
      name: $("#resName").value.trim(),
      source: $("#resSource").value,
      destination: $("#resDest").value,
      date: $("#resDate").value
    };
    if (!data.name || !data.date) return toast("Please fill in name and date.", "error");
    if (data.source === data.destination) return toast("Source and destination must differ.", "error");

    const btn = $("#resSubmit");
    setBusy(btn, true, "Reserving…");
    try {
      const r = await Api.createReservation(data);
      toast(`Reservation confirmed. PNR ${r.pnr}`, "success");
      $("#resName").value = "";
      await load();
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setBusy(btn, false);
    }
  }

  async function cancel(id) {
    if (!confirm(`Cancel reservation #${id}?`)) return;
    try {
      await Api.cancelReservation(id);
      toast(`Reservation #${id} cancelled.`, "success");
      await load();
    } catch (err) {
      toast(err.message, "error");
    }
  }

  function init() {
    const nodes = App.topology.nodes.map(n => ({ value: n, label: n }));
    fillSelect($("#resSource"), nodes, "Delhi");
    fillSelect($("#resDest"), nodes, "Server");
    $("#resDate").min = today();
    $("#resDate").value = today();

    $("#reservationForm").addEventListener("submit", submit);
    $("#resSource").addEventListener("change", previewRoute);
    $("#resDest").addEventListener("change", previewRoute);
    $("#resSearch").addEventListener("input", render);
    $("#resFilter").addEventListener("change", render);
    $("#resRefresh").addEventListener("click", load);
    $("#resBody").addEventListener("click", e => {
      const id = e.target.dataset && e.target.dataset.cancel;
      if (id) cancel(id);
    });

    previewRoute();
    load();
  }

  return { init, load };
})();
