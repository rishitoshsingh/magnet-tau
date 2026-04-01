```mermaid
graph LR
  n0["GetAppointmentDetails"]
  style n0 fill:#ffe599,stroke:#333,stroke-width:1px
  n1["GetProviderDetails"]
  style n1 fill:#ffe599,stroke:#333,stroke-width:1px
  n2["GetMedicalRecord"]
  style n2 fill:#ffe599,stroke:#333,stroke-width:1px
  n3["GetPatientTelemetryDevices"]
  style n3 fill:#ffe599,stroke:#333,stroke-width:1px
  n4["GetRegimenOptions"]
  style n4 fill:#ffe599,stroke:#333,stroke-width:1px
  n5["ListPatientMedicalRecords"]
  style n5 fill:#ffe599,stroke:#333,stroke-width:1px
  n6["ListAvailableProviders"]
  style n6 fill:#ffe599,stroke:#333,stroke-width:1px
  n7["ListPatientAppointments"]
  style n7 fill:#ffe599,stroke:#333,stroke-width:1px
  n8["ListMedicationSuppliers"]
  style n8 fill:#ffe599,stroke:#333,stroke-width:1px
  n9["ListTelemetryUploads"]
  n10["CheckDrugInteractions"]
  style n10 fill:#ffe599,stroke:#333,stroke-width:1px
  n11["ScheduleAppointment"]
  style n11 fill:#ffe599,stroke:#333,stroke-width:1px
  n12["CancelAppointment"]
  style n12 fill:#ffe599,stroke:#333,stroke-width:1px
  n13["RescheduleAppointment"]
  style n13 fill:#ffe599,stroke:#333,stroke-width:1px
  n14["UpdatePrescriptionSupplier"]
  n15["ListTelemetryDevices"]
  style n15 fill:#ffe599,stroke:#333,stroke-width:1px
  n16["GetTelemetryUpload"]
  n17["UpdateMedicalRecordNote"]
  n0 --> n1
  n0 --> n2
  n0 --> n5
  n0 --> n11
  n0 --> n12
  n1 --> n5
  n1 --> n11
  n1 --> n12
  n2 --> n0
  n2 --> n3
  n2 --> n6
  n2 --> n16
  n2 --> n17
  n3 --> n4
  n3 --> n14
  n3 --> n15
  n4 --> n2
  n4 --> n3
  n5 --> n0
  n5 --> n2
  n5 --> n3
  n5 --> n6
  n5 --> n16
  n5 --> n17
  n6 --> n1
  n6 --> n11
  n6 --> n12
  n7 --> n0
  n7 --> n1
  n7 --> n2
  n7 --> n3
  n7 --> n9
  n7 --> n10
  n7 --> n11
  n8 --> n10
  n8 --> n12
  n9 --> n3
  n9 --> n14
  n9 --> n16
  n10 --> n2
  n10 --> n4
  n11 --> n0
  n11 --> n1
  n11 --> n5
  n11 --> n8
  n12 --> n0
  n12 --> n2
  n12 --> n6
  n12 --> n11
  n13 --> n0
  n13 --> n1
  n13 --> n2
  n13 --> n7
  n13 --> n8
  n14 --> n2
  n14 --> n17
  n15 --> n3
  n15 --> n9
  n15 --> n14
  n15 --> n15
  n16 --> n3
  n16 --> n15
  n17 --> n2
```