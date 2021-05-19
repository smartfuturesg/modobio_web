delete from "LookupRoles" 
			where idx >= 1;
alter sequence "LookupRoles_idx_seq"
  restart with 1;

INSERT INTO "LookupRoles" ("created_at", "updated_at","role_name","display_name","alt_role_name","is_practitioner","color","icon","has_client_data_access","active") 

VALUES
('NOW()','NOW()','staff_admin','Staff Admin','Practioner Admin',False,'#000000',NULL,False,False),
('NOW()','NOW()','data_scientist','Data Scientist',NULL,False,'#000000',NULL,False,False),
('NOW()','NOW()','community_manager','Community Manager','ambassador',False,'#000000',NULL,False,False),
('NOW()','NOW()','physical_therapist','Physical Therapist','physiotherapist',True,'#fec619','physiotherapist.svg',True,False),
('NOW()','NOW()','dietitian','Dietitian',NULL,True,'#000000',NULL,True,False),
('NOW()','NOW()','nutritionist','Nutritionist',NULL,True,'#4661af','nutritionist - 1.svg',True,False),
('NOW()','NOW()','therapist','Therapist','psychologist',True,'#000000',NULL,True,False),
('NOW()','NOW()','nurse_practitioner','Nurse Practitioner',NULL,True,'#000000',NULL,True,False),
('NOW()','NOW()','nurse','Nurse',NULL,True,'#000000',NULL,True,False),
('NOW()','NOW()','physician_assistant','Physicians Assistant',NULL,True,'#000000',NULL,True,False),
('NOW()','NOW()','system_admin','System Admin',NULL,False,'#000000',NULL,False,True),
('NOW()','NOW()','client_services','Client Services',NULL,False,'#000000',NULL,True,True),
('NOW()','NOW()','medical_doctor','Medical medical_doctor','physician',True,'#d71e3e','medical_doctor.svg',True,True),
('NOW()','NOW()','trainer',	'Trainer','physical_trainer, personal_trainer',True,'#aef2ea','physical-training.svg',True,True);
