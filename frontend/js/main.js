// Bootstraps the app: checks the backend, loads the topology, wires tab navigation.
const PAGES = ["reservations", "network", "routing", "distance-vector", "link-failure", "protocols"];

function showPage(name) {
  if (!PAGES.includes(name)) name = "reservations";
  PAGES.forEach(p => $("#page-" + p).classList.toggle("hidden", p !== name));
  $$("#tabs a").forEach(a => a.classList.toggle("active", a.dataset.page === name));
}

function setStatus(online) {
  const el = $("#status");
  el.className = "status " + (online ? "status-online" : "status-offline");
  $("#statusText").textContent = online ? "Backend online" : "Backend offline";
  $("#offlineBanner").classList.toggle("hidden", online);
  $("#offlineUrl").textContent = Api.base();
}

async function boot() {
  try {
    await Api.ping();
    App.topology = await Api.topology();
  } catch (e) {
    setStatus(false);
    return;
  }
  setStatus(true);

  if (!boot.done) {
    boot.done = true;
    Reservations.init();
    Network.init();
    Routing.init();
    DistanceVector.init();
    LinkFailure.init();
    Protocols.init();
  } else {
    Reservations.load();
  }
}

window.addEventListener("hashchange", () => showPage(location.hash.slice(1)));
document.addEventListener("DOMContentLoaded", () => {
  showPage(location.hash.slice(1));
  $("#retryBtn").addEventListener("click", boot);
  $("#offlineUrl").textContent = Api.base();
  boot();
});
