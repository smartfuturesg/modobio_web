DELETE FROM "LookupClinicalCareTeamResources"
	WHERE resource_name='medications';

DELETE FROM "LookupClinicalCareTeamResources" 
	WHERE resource_id >= 1;
ALTER SEQUENCE "LookupClinicalCareTeamResources_resource_id_seq"
  RESTART WITH 1;

INSERT INTO "LookupClinicalCareTeamResources" ("resource_name", "display_name", "resource_group", "access_group") 
VALUES
('blood_chemistry', 'Blood Chemistry', null, 'medical_doctor'),
('blood_pressure', 'Blood Pressure', null, 'medical_doctor'),
('diagnostic_imaging', 'Diagnostic Imaging', null, 'medical_doctor'),
('sexual_history', 'Sexual History', 'medical_history', 'medical_doctor'),
('social_history', 'Social History', 'medical_history', 'medical_doctor'),
('general_medical_info', 'General Medical Information', 'medical_history', 'medical_doctor'),
('personal_medical_history', 'Personal Medical History','medical_history', 'medical_doctor'),
('wearable_data', 'Activity Tracker Data', null, 'general'),
('identity_profile', 'Identity Profile', null, 'general'),
('health_profile', 'Health Profile', null, 'general');