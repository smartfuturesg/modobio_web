--add operational territories for seed users pro@modobio.com and name@modobio.com

delete from "PractitionerOrganizationAffiliation" 
			where idx >= 1;
alter sequence "PractitionerOrganizationAffiliation_idx_seq"
  restart with 1;


insert into "PractitionerOrganizationAffiliation" ("user_id", "organization_idx", "affiliate_user_id") values
(30, 1, 'a98f3ccb-093c-4831-a612-8d403589ae9f'),
(31, 1, 'b1501b2b-5995-4cc1-8d5d-d982804c7aad'),
(32, 1, 'b0f78e0c-cb3f-4708-b632-8e2b3fd23507'),
(33, 1, '67ab1245-7145-42ab-accf-41120e1e55af');

