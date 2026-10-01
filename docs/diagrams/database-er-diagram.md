# Railway Reservation System - Database ER Diagram

## Entity Relationship Diagram

```text
+-----------------------------+
|           TRAINS            |
+-----------------------------+
| PK train_number             |
|    train_name               |
|    source                   |
|    destination              |
|    total_seats              |
+-----------------------------+
              |
              | 1
              |
              | 
              | many
              v
+-----------------------------+
|       RESERVATIONS          |
+-----------------------------+
| PK reservation_id           |
|    passenger_name           |
| FK train_number             |
|    source                   |
|    destination              |
|    seats                    |
+-----------------------------+
```

## Relationship

One train can have multiple reservations.

The `train_number` field in the `reservations` table is a foreign key that references `train_number` in the `trains` table.

### Trains

Stores information about available trains:

* Train number
* Train name
* Source station
* Destination station
* Total number of seats

### Reservations

Stores passenger reservation information:

* Reservation ID
* Passenger name
* Train number
* Source station
* Destination station
* Number of seats reserved
