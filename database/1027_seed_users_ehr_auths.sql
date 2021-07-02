--care team authorizations for seed users pro@modobio.com and name@modobio.com

delete from "ClientClinicalCareTeam" 
			where idx >= 1;
alter sequence "ClientClinicalCareTeam_idx_seq"
  restart with 1;

delete from "ClientEHRPageAuthorizations" 
			where idx >= 1;
alter sequence "ClientEHRPageAuthorizations_idx_seq"
  restart with 1;


insert into "ClientClinicalCareTeam" ("user_id", "team_member_user_id") values
(22, 10),
(22, 14);

insert into "ClientEHRPageAuthorizations" ("user_id", "team_member_user_id", "resource_group_id", "status") values
(22, 10, 1, 'accepted'),
(22, 10, 2, 'accepted'),
(22, 10, 3, 'accepted'),
(22, 10, 4, 'accepted'),
(22, 10, 5, 'accepted'),
(22, 10, 6, 'accepted'),
(22, 10, 7, 'accepted'),
(22, 10, 8, 'accepted'),
(22, 14, 1, 'accepted'),
(22, 14, 2, 'accepted'),
(22, 14, 3, 'accepted'),
(22, 14, 4, 'accepted'),
(22, 14, 5, 'accepted'),
(22, 14, 6, 'accepted'),
(22, 14, 7, 'accepted'),
(22, 14, 8, 'accepted');
(22, 14, 8, 'accepted');
(22, 14, 8, 'accepted');