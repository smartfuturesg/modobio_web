delete from "LookupClinicalCareTeamResources" 
			where resource_id >= 1;
alter sequence "LookupClinicalCareTeamResources_resource_id_seq"
  restart with 1;

INSERT INTO "LookupClinicalCareTeamResources" ("resource_name", "display_name") 
VALUES
('MedicalBloodTestResults', 'Blood Test Results'),
('MedicalBloodTests', 'Blood Tests'),
('MedicalConditions', 'Medical Conditions'),
('MedicalGeneralInfo', 'General Medical Information'),
('MedicalGeneralInfoMedications', 'Medications'),
('MedicalImaging', 'Medical Images'),
('MedicalSTDHistory', 'STD History'),
('MedicalSocialHistory', 'Social History'),
('MedicalSurgeries', 'Surgery History'),
('MedicalGeneralInfoMedicationAllergy', 'Medication Allergies'),
('MedicalFamilyHistory', 'Family Medical History'),
('MedicalBloodPressures', 'Blood Pressure Readings');