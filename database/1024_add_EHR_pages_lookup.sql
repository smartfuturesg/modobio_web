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


--care team authorizations for seed users pro@modobio.com and name@modobio.com

delete from "ClientClinicalCareTeam" 
			where idx >= 1;
alter sequence "ClientClinicalCareTeam_idx_seq"
  restart with 1;

delete from "ClientEHRPageAuthorizations" 
			where idx >= 1;
alter sequence "ClientEHRPageAuthorizations_idx_seq"
  restart with 1;


insert into "ClientClinicalCareTeam" ("user_id", "team_member_user_id") values
(22, 10),
(22, 14);

insert into "ClientEHRPageAuthorizations" ("user_id", "team_member_user_id", "resource_group_id", "status") values
(22, 10, 1, 'accepted'),
(22, 10, 2, 'accepted'),
(22, 10, 3, 'accepted'),
(22, 10, 4, 'accepted'),
(22, 10, 5, 'accepted'),
(22, 10, 6, 'accepted'),
(22, 10, 7, 'accepted'),
(22, 10, 8, 'accepted'),
(22, 14, 1, 'accepted'),
(22, 14, 2, 'accepted'),
(22, 14, 3, 'accepted'),
(22, 14, 4, 'accepted'),
(22, 14, 5, 'accepted'),
(22, 14, 6, 'accepted'),
(22, 14, 7, 'accepted'),
(22, 14, 8, 'accepted');