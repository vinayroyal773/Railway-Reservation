"""Run from the project root:  python tests/test_server.py  (starts its own server on port 5057)"""
import json, os, sys, tempfile, threading, urllib.request, urllib.error
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["RAILWAY_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
import server

BASE = "http://127.0.0.1:5057"


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def main():
    srv = server.make_server(port=5057)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    s, d = call("GET", "/api/topology"); assert s == 200 and "Server" in d["nodes"]
    s, d = call("POST", "/api/route", {"source": "Delhi", "destination": "Server"}); assert s == 200 and d["path"][-1] == "Server"
    s, d = call("POST", "/api/crc", {"message": "1011001", "generator": "1101"}); assert s == 200
    s, d = call("POST", "/api/go-back-n", {"packets": 8, "window_size": 3, "lost_packet": 3}); assert s == 200
    s, d = call("POST", "/api/go-back-n", {"packets": 8, "lost_packet": 99}); assert s == 400

    s, d = call("POST", "/api/reservations", {"name": "Asha", "source": "Delhi", "destination": "Server", "date": "2026-11-05"})
    assert s == 201 and len(d["pnr"]) == 10; rid = d["id"]
    s, d = call("POST", "/api/reservations", {"name": "X", "source": "Delhi", "destination": "Delhi", "date": "2026-11-05"}); assert s == 400
    s, d = call("GET", "/api/reservations?q=asha"); assert s == 200 and d[0]["name"] == "Asha"
    s, d = call("DELETE", f"/api/reservations/{rid}"); assert s == 200
    s, d = call("DELETE", f"/api/reservations/{rid}"); assert s == 409
    s, d = call("DELETE", "/api/reservations/999"); assert s == 404

    s, d = call("POST", "/api/link-failure", {"from": "Nagpur", "to": "Server"}); assert s == 200 and d["new_path"]
    s, d = call("POST", "/api/distance-vector", {"fail": ["Nagpur", "Server"]}); assert s == 200
    s, d = call("GET", "/api/events"); assert s == 200 and len(d) == 4
    s, d = call("POST", "/api/performance", {"protocol": "go_back_n", "packets_sent": 100, "packets_lost": 5, "delay_ms": 1000, "window_size": 8}); assert s == 201
    s, d = call("GET", "/api/performance"); assert d["summary"][0]["runs"] == 1
    s, d = call("GET", "/api/stats"); assert d["confirmed"] == 0 and d["cancelled"] == 1
    s, d = call("GET", "/api/nope"); assert s == 404

    with urllib.request.urlopen(BASE + "/") as r:
        assert r.status == 200 and b"Railway" in r.read()
    with urllib.request.urlopen(BASE + "/js/api.js") as r:
        assert r.status == 200
    print("ok   all server tests passed")
    srv.shutdown()


if __name__ == "__main__":
    main()
