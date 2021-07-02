delete from "LookupClinicalCareTeamResources" 
			where resource_id >= 1;
alter sequence "LookupClinicalCareTeamResources_resource_id_seq"
  restart with 1;

INSERT INTO "LookupClinicalCareTeamResources" ("resource_name", "display_name", "resource_group_id") 
VALUES
('MedicalBloodTestResults', 'Blood Test Results', 8),
('MedicalBloodTests', 'Blood Tests', 8),
('MedicalConditions', 'Medical Conditions', 4),
('MedicalGeneralInfo', 'General Medical Information', 4),
('MedicalGeneralInfoMedications', 'Medications', 5),
('MedicalImaging', 'Medical Images', 6),
('MedicalSTDHistory', 'STD History', 4),
('MedicalSocialHistory', 'Social History', 4),
('MedicalGeneralInfoMedicationAllergy', 'Medication Allergies', 5),
('MedicalFamilyHistory', 'Family Medical History', 4),
('ClientWeightHistory', 'Weight History', 2),
('ClientHeightHistory', 'Height History', 2),
('ClientWaistSizeHistory', 'Waist Size History', 2),
('ClientRaceAndEthnicity', 'Race and Ethnicity', 2),
('ClientInfo', 'Client General Information', 1),
('WearablesDataDynamo', 'Activity Tracker Data', 3),
('MedicalBloodPressures', 'Blood Pressure Readings', 7);