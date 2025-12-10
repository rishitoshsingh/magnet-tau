```mermaid
graph LR
    n0["BookReservation"]
    n1["Calculate"]
    n2["CancelReservation"]
    n3["GetReservationDetails"]
    n4["GetUserDetails"]
    n5["ListAllAirports"]
    n6["SearchDirectFlight"]
    n7["SearchOnestopFlight"]
    n8["SendCertificate"]
    n9["TransferToHumanAgents"]
    n10["UpdateReservationBaggages"]
    n11["UpdateReservationFlights"]
    n12["UpdateReservationPassengers"]
    n0 --> n2
    n0 --> n3
    n0 --> n9
    n0 --> n10
    n0 --> n11
    n0 --> n12
    n2 --> n0
    n2 --> n3
    n2 --> n6
    n2 --> n7
    n2 --> n8
    n2 --> n9
    n3 --> n2
    n3 --> n4
    n3 --> n6
    n3 --> n7
    n3 --> n8
    n3 --> n9
    n3 --> n10
    n3 --> n11
    n3 --> n12
    n4 --> n0
    n4 --> n2
    n4 --> n3
    n4 --> n8
    n4 --> n9
    n4 --> n10
    n4 --> n11
    n4 --> n12
    n5 --> n0
    n5 --> n6
    n5 --> n7
    n6 --> n0
    n7 --> n0
    n7 --> n9
    n8 --> n0
    n8 --> n10
    n8 --> n11
    n10 --> n3
    n10 --> n9
    n11 --> n2
    n11 --> n3
    n11 --> n9
    n11 --> n10
    n11 --> n12
    n12 --> n2
    n12 --> n3
    n12 --> n9
    n12 --> n10
    n12 --> n11
```