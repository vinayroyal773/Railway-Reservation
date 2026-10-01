# Railway Reservation System - System Architecture

## Overview

The Railway Reservation System is divided into four main layers:

```text
                    Railway Reservation System
                              |
          +-------------------+-------------------+
          |                   |                   |
      Frontend             Backend             Network
          |                   |                   |
    index.html          reservation.java      Routing.java
    script.js           server.java            Dijkstra
    style.css           errorDetection.java
                        errorRecovery.java
                              |
                              |
                         Database Layer
                              |
                         railway.db
                              |
                 +------------+------------+
                 |                         |
              trains                 reservations
```

## Data Flow

```text
User
 |
 v
Frontend
 |
 v
Backend
 |
 +---------> Error Detection
 |
 +---------> Error Recovery
 |
 +---------> Database
 |
 +---------> Railway Routing
 |
 v
Response to User
```
