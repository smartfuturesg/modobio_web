delete from "LookupRoles" 
			where idx >= 1;
alter sequence "LookupRoles_idx_seq"
  restart with 1;

INSERT INTO "LookupRoles" ("created_at", "updated_at","role_name","display_name","alt_role_name","icon","is_practitioner","has_client_data_access","active") 

VALUES
('NOW()','NOW()','beautician','Beautician','esthetician','Beautician.svg',True,True,False),
('NOW()','NOW()','chef','Chef',NULL,'ChefP.svg',True,True,True),
('NOW()','NOW()','client_services','Client Services',NULL,'CommunityM.svg',False,True,True),
('NOW()','NOW()','community_manager','Community Manager','ambassador',NULL,False,False,True),
('NOW()','NOW()','data_scientist','Data Scientist',NULL,NULL,False,False,False),
('NOW()','NOW()','dietitian','Dietitian',NULL,'DietitianP.svg',True,True,True),
('NOW()','NOW()','medical_doctor','Medical Doctor','physician, clinician','MedicalDoctorP.svg',True,True,True),
('NOW()','NOW()','nurse','Nurse',NULL,'NurseP.svg',True,True,False),
('NOW()','NOW()','nutritionist','Nutritionist',NULL,NULL,True,True,False),
('NOW()','NOW()','physical_therapist','Physical Therapist','physiotherapist','PhysicalTherapistP.svg',True,True,False),
('NOW()','NOW()','staff_admin','Staff Admin','practitioner_admin','SystemAdmin.svg',False,False,True),
('NOW()','NOW()','system_admin','System Admin',NULL,NULL,False,False,True),
('NOW()','NOW()','therapist','Therapist','mental_health_specialist','Therapist.svg',True,True,True),
('NOW()','NOW()','trainer','Trainer','physical_trainer, personal_trainer','TrainerP.svg',True,True,True);