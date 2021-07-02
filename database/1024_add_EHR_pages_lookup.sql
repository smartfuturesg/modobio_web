delete from "LookupEHRPages" 
			where resource_group_id >= 1;
alter sequence "LookupEHRPages_resource_group_id_seq"
  restart with 1;

INSERT INTO "LookupEHRPages" ("resource_group_id", "resource_group_name", "display_name", "access_group") 
VALUES
(1, 'identity_profile', 'Identity Profile' , 'general'),
(2, 'health_profile', 'Health Profile' , 'general'),
(3, 'activity_tracker', 'Activity Tracker Data' , 'general'),
(4, 'medical_history', 'Medical History' , 'medical_doctor'),
(5, 'medications', 'Medications' , 'medical_doctor'),
(6, 'diagnostic_imaging', 'Diagnostic Imaging' , 'medical_doctor'),
(7, 'blood_pressure', 'Blood Pressure' , 'medical_doctor'),
(8, 'blood_chemistry', 'Blood Chemistry' , 'medical_doctor');