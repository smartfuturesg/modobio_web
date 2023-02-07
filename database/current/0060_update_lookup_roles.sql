

DELETE FROM "LookupRoles"
WHERE role_name = 'nurse';

INSERT INTO "LookupRoles"
(role_name, display_name, alt_role_name, is_practitioner, color, icon, active, notes, is_provider, rpm_enroll, rpm_support, telehealth_access)
VALUES
('nurse_practitioner', 'Nurse Practitioner', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, true, true, true),
('certified_nurse_specialist', 'Certified Nurse Specialist', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, true, true, true),
('physician_assistant', 'Physician Assistant', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, true, true, true),
('certified_nurse_midwife', 'Certified Nurse Midwife', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, true, true, true),
('certified_registered_nurse', 'Certified Registered Nurse Anesthetist', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, true, true, true),
('medical_assistant', 'Medical Assistant', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, false, true, true),
('licensed_practical_nurse', 'Licensed Practical Nurse', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, false, true, true),
('registered_nurse', 'Registered Nurse', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, false, true, true),
('care_coordinator', 'Care Coordinator', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, false, true, true), 
('care_manager', 'Care Manager', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, false, true, true),
('case_manager', 'Case Manager', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, false, true, true),
('patient_advocate', 'Patient Advocate', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, false, true, true),
('patient_navigator', 'Patient Navigator ', NULL, NULL, NULL, 'MedicalDoctorP.svg', true, NULL, true, false, true, true);


UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'beautician';

UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'chef';

UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'client_services';

UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'community_manager';

UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'data_scientist';

UPDATE "LookupRoles"
SET telehealth_access = true, rpm_enroll = false, rpm_support = false
WHERE role_name = 'dietitian';

UPDATE "LookupRoles"
SET telehealth_access = true, rpm_enroll = true, rpm_support = true
WHERE role_name = 'medical_doctor';

UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'nutritionist';

UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'physical_therapist';

UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'staff_admin';

UPDATE "LookupRoles"
SET telehealth_access = false, rpm_enroll = false, rpm_support = false
WHERE role_name = 'system_admin';

UPDATE "LookupRoles"
SET telehealth_access = true, rpm_enroll = false, rpm_support = false
WHERE role_name = 'therapist';

UPDATE "LookupRoles"
SET telehealth_access = true, rpm_enroll = false, rpm_support = false
WHERE role_name = 'trainer';

