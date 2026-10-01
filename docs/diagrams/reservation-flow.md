# Railway Reservation System - Reservation Flow

## Reservation Process

```text
+------------------+
|      User        |
+------------------+
         |
         v
+------------------+
| Enter Passenger  |
|     Details      |
+------------------+
         |
         v
+------------------+
| Validate Details |
+------------------+
         |
         v
    +---------+
    | Valid?  |
    +---------+
      |     |
    No|     |Yes
      |     |
      v     v
+----------+  +------------------+
|  Error   |  | Check Train      |
| Message  |  | Availability     |
+----------+  +------------------+
      |              |
      |              v
      |       +-------------+
      |       | Seats       |
      |       | Available?  |
      |       +-------------+
      |          |       |
      |        No|       |Yes
      |          |       |
      |          v       v
      |      +-------+  +----------------+
      |      | Error |  | Save           |
      |      | Message| | Reservation    |
      |      +-------+  +----------------+
      |                       |
      |                       v
      |                +-------------+
      |                | Reservation |
      |                | Confirmed   |
      |                +-------------+
      |                       |
      +-----------------------+
```

## Process Description

1. The user enters passenger and journey details.
2. The system validates the entered information.
3. Invalid information produces an error message.
4. Valid information is used to check train availability.
5. If seats are unavailable, the system displays an error.
6. If seats are available, the reservation is stored in the database.
7. The system confirms the reservation.
