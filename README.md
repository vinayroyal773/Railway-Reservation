# Reliable Railway Reservation Network Using Routing and Error Recovery

Starter full-stack academic project.

## Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python + Flask
- Database: SQLite
- Networking: Dijkstra, Distance Vector, CRC, Sliding Window, Go-Back-N, Link Failure

## Run backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

Open frontend/index.html in a browser.

Backend default:
http://127.0.0.1:5000

## Project structure
frontend/     User interface
backend/      Flask APIs and networking algorithms
database/     SQLite database
simulation/   Performance/network simulation helpers
docs/         Project documentation

## Database (SQLite)
Schema: `database/schema.sql`. Data access: `backend/db.py`.
Tables: `stations`, `links`, `reservations` (PNR, route, status, timestamps),
`network_events` (link failures, route changes), `performance_runs` (loss/delay/throughput).

    python database/init_db.py            # create or upgrade (keeps existing reservations)
    python database/init_db.py --reset --demo   # fresh DB with sample data
    python tests/test_database.py

Extra API: GET /api/stats, GET /api/events, GET/POST /api/performance,
GET /api/reservations?status=CONFIRMED&q=asha

