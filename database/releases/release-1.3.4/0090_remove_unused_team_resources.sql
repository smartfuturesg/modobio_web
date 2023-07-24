-- Remove unused items from LookupClinicalCareTeamResources table (NRV-4123).
-- This reverses release-1.2.2a/0050_add_clinical_care_resources.sql
--
-- Entries in ClientClinicalCareTeamAuthorizations with a reference to
-- LookupClinicalCareTeamResources.resource_id will be cascade-deleted.

DELETE FROM "LookupClinicalCareTeamResources"
    WHERE resource_name IN (
        'team',
        'medical_doctor_appointments',
        'dietitian_appointments',
        'nutritionist_appointments',
        'physical_therapist_appointments',
        'therapist_appointments',
        'trainer_appointments',
        'beautician_appointments',
        'chef_appointments',
        'nurse_appointments',
        'medical_doctor_history',
        'dietitian_history',
        'nutritionist_history',
        'physical_therapist_history',
        'therapist_history',
        'trainer_history',
        'beautician_history',
        'chef_history',
        'nurse_history');

-- fitness_goals was defined twice, in release-1.2.1/0040_update_team_resources.sql
-- and in release-1.2.2a/0050_add_clinical_care_resources.sql. Delete the second one.
DELETE FROM "LookupClinicalCareTeamResources"
    WHERE resource_name = 'fitness_goals'
    AND resource_group = 'trainer';
