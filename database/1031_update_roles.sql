--remove roles that no longer exist
DELETE FROM "LookupRoles" WHERE 'role_name' = 'nurse_practitioner';
DELETE FROM "LookupRoles" WHERE 'role_name' = 'physician_assistant';

--remove notion of color
UPDATE "LookupRoles" SET 'color' = NULL;

--insert new roles
INSERT INTO "LookupRoles" ("created_at", "updated_at","role_name","display_name","alt_role_name","icon","is_practitioner","has_client_data_access","active") 
VALUES
('NOW()','NOW()','beautician','Beautician','esthetician','Beautician.svg',True,True,False),
('NOW()','NOW()','chef','Chef',NULL,'ChefP.svg',True,True,True);

--update roles active flags
UPDATE "LookupRoles" SET 'active' = True WHERE "role_name" IN ('client_services','community_manager','dietitian','medical_doctor','staff_admin','system_admin','therapist','trainer');
UPDATE "LookupRoles" SET 'active' = False WHERE "role_name" IN ('data_scientist', 'nurse', 'nutritionist', 'physical_therapist');