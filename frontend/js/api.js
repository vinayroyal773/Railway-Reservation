// Thin wrapper over the Flask API. Every method returns parsed JSON or throws ApiError.
class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

const Api = (() => {
  const base = () => window.APP_CONFIG.API_BASE.replace(/\/$/, "");

  async function request(path, { method = "GET", body } = {}) {
    let res;
    try {
      res = await fetch(base() + path, {
        method,
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined
      });
    } catch (e) {
      throw new ApiError("Cannot reach the backend. Is the Flask server running?", 0);
    }
    let data = null;
    try { data = await res.json(); } catch (e) { /* non-JSON response */ }
    if (!res.ok) {
      throw new ApiError((data && data.error) || `Request failed (${res.status})`, res.status);
    }
    return data;
  }

  const post = (path, body) => request(path, { method: "POST", body });

  return {
    base,
    ping: () => request("/"),
    topology: () => request("/api/topology"),
    route: (source, destination) => post("/api/route", { source, destination }),
    routingTable: node => request("/api/routing-table/" + encodeURIComponent(node)),
    distanceVector: (poison_reverse, fail) => post("/api/distance-vector", { poison_reverse, fail }),
    crc: (message, generator) => post("/api/crc", { message, generator }),
    slidingWindow: (packets, window_size) => post("/api/sliding-window", { packets, window_size }),
    goBackN: (packets, window_size, lost_packet) => post("/api/go-back-n", { packets, window_size, lost_packet }),
    linkFailure: (from, to, source, destination) => post("/api/link-failure", { from, to, source, destination }),
    listReservations: () => request("/api/reservations"),
    createReservation: data => post("/api/reservations", data),
    cancelReservation: id => request("/api/reservations/" + id, { method: "DELETE" })
  };
})();
