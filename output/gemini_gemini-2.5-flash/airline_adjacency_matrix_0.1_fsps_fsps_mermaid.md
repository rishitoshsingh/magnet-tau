# FSP Visualizations for `airline_adjacency_matrix_0.1_fsps.json`


## FSP #0


### Variant: `base`

```mermaid
graph LR
    %% FSP_0_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationBaggages"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["UpdateReservationFlights"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["CancelReservation"]
        t2_n5["TransferToHumanAgents"]
        t2_n4 --> t2_n5
    end
    t0_n2 --> t1_n3
    t1_n3 --> t2_n4
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_0_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationBaggages"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["UpdateReservationFlights"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["MISSING(miss_params)"]
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n5["CancelReservation"]
        t3_n6["TransferToHumanAgents"]
        t3_n5 --> t3_n6
    end
    t0_n2 --> t1_n3
    t1_n3 --> t2_n4
    t2_n4 --> t3_n5
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_0_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationBaggages"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["MISSING(miss_func)"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["UpdateReservationFlights"]
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n5["CancelReservation"]
        t3_n6["TransferToHumanAgents"]
        t3_n5 --> t3_n6
    end
    t0_n2 --> t1_n3
    t1_n3 --> t2_n4
    t2_n4 --> t3_n5
```


## FSP #1


### Variant: `base`

```mermaid
graph LR
    %% FSP_1_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["GetReservationDetails"]
        t0_n1["SearchOnestopFlight"]
        t0_n0 --> t0_n1
        t0_n2["BookReservation"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["BookReservation"]
        t1_n4["UpdateReservationBaggages"]
        t1_n3 --> t1_n4
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n5["UpdateReservationFlights"]
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n6["BookReservation"]
        t3_n7["CancelReservation"]
        t3_n6 --> t3_n7
    end
    t0_n2 --> t1_n3
    t1_n4 --> t2_n5
    t2_n5 --> t3_n6
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_1_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["GetReservationDetails"]
        t0_n1["SearchOnestopFlight"]
        t0_n0 --> t0_n1
        t0_n2["BookReservation"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["BookReservation"]
        t1_n4["UpdateReservationBaggages"]
        t1_n3 --> t1_n4
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n5["UpdateReservationFlights"]
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n6["BookReservation"]
        t3_n7["CancelReservation"]
        t3_n6 --> t3_n7
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n8["MISSING(miss_params)"]
    end
    t0_n2 --> t1_n3
    t1_n4 --> t2_n5
    t2_n5 --> t3_n6
    t3_n7 --> t4_n8
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_1_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["GetReservationDetails"]
        t0_n1["SearchOnestopFlight"]
        t0_n0 --> t0_n1
        t0_n2["BookReservation"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["BookReservation"]
        t1_n4["UpdateReservationBaggages"]
        t1_n3 --> t1_n4
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n5["UpdateReservationFlights"]
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n6["MISSING(miss_func)"]
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n7["BookReservation"]
        t4_n8["CancelReservation"]
        t4_n7 --> t4_n8
    end
    t0_n2 --> t1_n3
    t1_n4 --> t2_n5
    t2_n5 --> t3_n6
    t3_n6 --> t4_n7
```


## FSP #2


### Variant: `base`

```mermaid
graph LR
    %% FSP_2_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["CancelReservation"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["TransferToHumanAgents"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["UpdateReservationFlights"]
    end
    t0_n2 --> t1_n3
    t1_n3 --> t2_n4
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_2_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["CancelReservation"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["TransferToHumanAgents"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["MISSING(miss_params)"]
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n5["UpdateReservationFlights"]
    end
    t0_n2 --> t1_n3
    t1_n3 --> t2_n4
    t2_n4 --> t3_n5
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_2_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["CancelReservation"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["TransferToHumanAgents"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["MISSING(miss_func)"]
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n5["UpdateReservationFlights"]
    end
    t0_n2 --> t1_n3
    t1_n3 --> t2_n4
    t2_n4 --> t3_n5
```


## FSP #3


### Variant: `base`

```mermaid
graph LR
    %% FSP_3_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SearchDirectFlight"]
        t0_n1["BookReservation"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["BookReservation"]
        t1_n3["CancelReservation"]
        t1_n2 --> t1_n3
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["UpdateReservationFlights"]
        t2_n5["GetReservationDetails"]
        t2_n4 --> t2_n5
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n6["TransferToHumanAgents"]
    end
    t0_n1 --> t1_n2
    t1_n3 --> t2_n4
    t2_n5 --> t3_n6
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_3_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SearchDirectFlight"]
        t0_n1["BookReservation"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["MISSING(miss_params)"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n3["BookReservation"]
        t2_n4["CancelReservation"]
        t2_n3 --> t2_n4
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n5["UpdateReservationFlights"]
        t3_n6["GetReservationDetails"]
        t3_n5 --> t3_n6
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n7["TransferToHumanAgents"]
    end
    t0_n1 --> t1_n2
    t1_n2 --> t2_n3
    t2_n4 --> t3_n5
    t3_n6 --> t4_n7
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_3_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SearchDirectFlight"]
        t0_n1["BookReservation"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["BookReservation"]
        t1_n3["CancelReservation"]
        t1_n2 --> t1_n3
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["UpdateReservationFlights"]
        t2_n5["GetReservationDetails"]
        t2_n4 --> t2_n5
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n6["MISSING(miss_func)"]
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n7["TransferToHumanAgents"]
    end
    t0_n1 --> t1_n2
    t1_n3 --> t2_n4
    t2_n5 --> t3_n6
    t3_n6 --> t4_n7
```


## FSP #4


### Variant: `base`

```mermaid
graph LR
    %% FSP_4_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SearchOnestopFlight"]
        t0_n1["TransferToHumanAgents"]
        t0_n0 --> t0_n1
    end
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_4_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SearchOnestopFlight"]
        t0_n1["TransferToHumanAgents"]
        t0_n0 --> t0_n1
    end
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_4_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SearchOnestopFlight"]
        t0_n1["TransferToHumanAgents"]
        t0_n0 --> t0_n1
    end
```


## FSP #5


### Variant: `base`

```mermaid
graph LR
    %% FSP_5_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["ListAllAirports"]
        t0_n1["BookReservation"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["BookReservation"]
        t1_n3["GetReservationDetails"]
        t1_n2 --> t1_n3
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["UpdateReservationPassengers"]
        t2_n5["TransferToHumanAgents"]
        t2_n4 --> t2_n5
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n6["GetReservationDetails"]
        t3_n7["SearchDirectFlight"]
        t3_n6 --> t3_n7
    end
    t0_n1 --> t1_n2
    t1_n3 --> t2_n4
    t2_n5 --> t3_n6
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_5_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["ListAllAirports"]
        t0_n1["BookReservation"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["BookReservation"]
        t1_n3["GetReservationDetails"]
        t1_n2 --> t1_n3
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["UpdateReservationPassengers"]
        t2_n5["TransferToHumanAgents"]
        t2_n4 --> t2_n5
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n6["MISSING(miss_params)"]
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n7["GetReservationDetails"]
        t4_n8["SearchDirectFlight"]
        t4_n7 --> t4_n8
    end
    t0_n1 --> t1_n2
    t1_n3 --> t2_n4
    t2_n5 --> t3_n6
    t3_n6 --> t4_n7
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_5_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["ListAllAirports"]
        t0_n1["BookReservation"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["BookReservation"]
        t1_n3["GetReservationDetails"]
        t1_n2 --> t1_n3
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n4["UpdateReservationPassengers"]
        t2_n5["TransferToHumanAgents"]
        t2_n4 --> t2_n5
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n6["GetReservationDetails"]
        t3_n7["SearchDirectFlight"]
        t3_n6 --> t3_n7
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n8["MISSING(miss_func)"]
    end
    t0_n1 --> t1_n2
    t1_n3 --> t2_n4
    t2_n5 --> t3_n6
    t3_n7 --> t4_n8
```


## FSP #6


### Variant: `base`

```mermaid
graph LR
    %% FSP_6_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationPassengers"]
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n1["CancelReservation"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n2["GetReservationDetails"]
        t2_n3["CancelReservation"]
        t2_n2 --> t2_n3
    end
    t0_n0 --> t1_n1
    t1_n1 --> t2_n2
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_6_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationPassengers"]
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n1["CancelReservation"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n2["MISSING(miss_params)"]
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n3["GetReservationDetails"]
        t3_n4["CancelReservation"]
        t3_n3 --> t3_n4
    end
    t0_n0 --> t1_n1
    t1_n1 --> t2_n2
    t2_n2 --> t3_n3
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_6_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationPassengers"]
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n1["CancelReservation"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n2["GetReservationDetails"]
        t2_n3["CancelReservation"]
        t2_n2 --> t2_n3
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n4["MISSING(miss_func)"]
    end
    t0_n0 --> t1_n1
    t1_n1 --> t2_n2
    t2_n3 --> t3_n4
```


## FSP #7


### Variant: `base`

```mermaid
graph LR
    %% FSP_7_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationBaggages"]
        t0_n1["TransferToHumanAgents"]
        t0_n0 --> t0_n1
    end
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_7_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationBaggages"]
        t0_n1["TransferToHumanAgents"]
        t0_n0 --> t0_n1
    end
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_7_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["UpdateReservationBaggages"]
        t0_n1["TransferToHumanAgents"]
        t0_n0 --> t0_n1
    end
```


## FSP #8


### Variant: `base`

```mermaid
graph LR
    %% FSP_8_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["CancelReservation"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["UpdateReservationFlights"]
        t1_n4["GetReservationDetails"]
        t1_n3 --> t1_n4
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n5["UpdateReservationPassengers"]
        t2_n6["GetReservationDetails"]
        t2_n5 --> t2_n6
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n7["UpdateReservationFlights"]
        t3_n8["GetReservationDetails"]
        t3_n7 --> t3_n8
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n9["GetReservationDetails"]
        t4_n10["UpdateReservationPassengers"]
        t4_n9 --> t4_n10
    end
    t0_n2 --> t1_n3
    t1_n4 --> t2_n5
    t2_n6 --> t3_n7
    t3_n8 --> t4_n9
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_8_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["CancelReservation"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["UpdateReservationFlights"]
        t1_n4["GetReservationDetails"]
        t1_n3 --> t1_n4
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n5["UpdateReservationPassengers"]
        t2_n6["GetReservationDetails"]
        t2_n5 --> t2_n6
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n7["UpdateReservationFlights"]
        t3_n8["GetReservationDetails"]
        t3_n7 --> t3_n8
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n9["MISSING(miss_params)"]
    end
    subgraph Turn_5 ["Turn 5"]
        direction LR
        t5_n10["GetReservationDetails"]
        t5_n11["UpdateReservationPassengers"]
        t5_n10 --> t5_n11
    end
    t0_n2 --> t1_n3
    t1_n4 --> t2_n5
    t2_n6 --> t3_n7
    t3_n8 --> t4_n9
    t4_n9 --> t5_n10
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_8_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["CancelReservation"]
        t0_n1["GetReservationDetails"]
        t0_n0 --> t0_n1
        t0_n2["UpdateReservationFlights"]
        t0_n1 --> t0_n2
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n3["UpdateReservationFlights"]
        t1_n4["GetReservationDetails"]
        t1_n3 --> t1_n4
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n5["UpdateReservationPassengers"]
        t2_n6["GetReservationDetails"]
        t2_n5 --> t2_n6
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n7["UpdateReservationFlights"]
        t3_n8["GetReservationDetails"]
        t3_n7 --> t3_n8
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n9["GetReservationDetails"]
        t4_n10["UpdateReservationPassengers"]
        t4_n9 --> t4_n10
    end
    subgraph Turn_5 ["Turn 5"]
        direction LR
        t5_n11["MISSING(miss_func)"]
    end
    t0_n2 --> t1_n3
    t1_n4 --> t2_n5
    t2_n6 --> t3_n7
    t3_n8 --> t4_n9
    t4_n10 --> t5_n11
```


## FSP #9


### Variant: `base`

```mermaid
graph LR
    %% FSP_9_base
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SendCertificate"]
        t0_n1["UpdateReservationFlights"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["UpdateReservationBaggages"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n3["UpdateReservationFlights"]
        t2_n4["GetReservationDetails"]
        t2_n3 --> t2_n4
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n5["GetReservationDetails"]
        t3_n6["GetUserDetails"]
        t3_n5 --> t3_n6
        t3_n7["UpdateReservationFlights"]
        t3_n6 --> t3_n7
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n8["GetReservationDetails"]
        t4_n9["UpdateReservationFlights"]
        t4_n8 --> t4_n9
    end
    t0_n1 --> t1_n2
    t1_n2 --> t2_n3
    t2_n4 --> t3_n5
    t3_n7 --> t4_n8
```


### Variant: `miss_params`

```mermaid
graph LR
    %% FSP_9_miss_params
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SendCertificate"]
        t0_n1["UpdateReservationFlights"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["UpdateReservationBaggages"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n3["UpdateReservationFlights"]
        t2_n4["GetReservationDetails"]
        t2_n3 --> t2_n4
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n5["GetReservationDetails"]
        t3_n6["GetUserDetails"]
        t3_n5 --> t3_n6
        t3_n7["UpdateReservationFlights"]
        t3_n6 --> t3_n7
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n8["GetReservationDetails"]
        t4_n9["UpdateReservationFlights"]
        t4_n8 --> t4_n9
    end
    subgraph Turn_5 ["Turn 5"]
        direction LR
        t5_n10["MISSING(miss_params)"]
    end
    t0_n1 --> t1_n2
    t1_n2 --> t2_n3
    t2_n4 --> t3_n5
    t3_n7 --> t4_n8
    t4_n9 --> t5_n10
```


### Variant: `miss_func`

```mermaid
graph LR
    %% FSP_9_miss_func
    subgraph Turn_0 ["Turn 0"]
        direction LR
        t0_n0["SendCertificate"]
        t0_n1["UpdateReservationFlights"]
        t0_n0 --> t0_n1
    end
    subgraph Turn_1 ["Turn 1"]
        direction LR
        t1_n2["UpdateReservationBaggages"]
    end
    subgraph Turn_2 ["Turn 2"]
        direction LR
        t2_n3["UpdateReservationFlights"]
        t2_n4["GetReservationDetails"]
        t2_n3 --> t2_n4
    end
    subgraph Turn_3 ["Turn 3"]
        direction LR
        t3_n5["MISSING(miss_func)"]
    end
    subgraph Turn_4 ["Turn 4"]
        direction LR
        t4_n6["GetReservationDetails"]
        t4_n7["GetUserDetails"]
        t4_n6 --> t4_n7
        t4_n8["UpdateReservationFlights"]
        t4_n7 --> t4_n8
    end
    subgraph Turn_5 ["Turn 5"]
        direction LR
        t5_n9["GetReservationDetails"]
        t5_n10["UpdateReservationFlights"]
        t5_n9 --> t5_n10
    end
    t0_n1 --> t1_n2
    t1_n2 --> t2_n3
    t2_n4 --> t3_n5
    t3_n5 --> t4_n6
    t4_n8 --> t5_n9
```
