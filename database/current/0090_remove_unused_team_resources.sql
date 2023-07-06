-- Remove unused items from LookupClinicalCareTeamResources table (NRV-4123)

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

-- fitness_goals was defined twice, so make sure we delete the correct one.
DELETE FROM "LookupClinicalCareTeamResources"
    WHERE resource_name = 'fitness_goals'
    AND resource_group = 'trainer';
