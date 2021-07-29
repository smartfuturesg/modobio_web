--care team authorizations for seed users pro@modobio.com and name@modobio.com

delete from "ClientClinicalCareTeam" 
			where idx >= 1;
alter sequence "ClientClinicalCareTeam_idx_seq"
  restart with 1;

delete from "ClientClinicalCareTeamAuthorizations" 
			where idx >= 1;
alter sequence "ClientClinicalCareTeamAuthorizations_idx_seq"
  restart with 1;


insert into "ClientClinicalCareTeam" ("user_id", "team_member_user_id", "is_temporary") values
(22, 10, false),
(22, 14, false);

insert into "ClientClinicalCareTeamAuthorizations" ("user_id", "team_member_user_id", "resource_id", "status") values
(22, 10, 1, 'accepted'),
(22, 10, 2, 'accepted'),
(22, 10, 3, 'accepted'),
(22, 10, 4, 'accepted'),
(22, 10, 5, 'accepted'),
(22, 10, 6, 'accepted'),
(22, 10, 7, 'accepted'),
(22, 10, 8, 'accepted'),
(22, 10, 9, 'accepted'),
(22, 10, 10, 'accepted'),
(22, 10, 11, 'accepted'),
(22, 10, 12, 'accepted'),
(22, 10, 13, 'accepted'),
(22, 10, 14, 'accepted'),
(22, 10, 15, 'accepted'),
(22, 10, 16, 'accepted'),
(22, 14, 1, 'accepted'),
(22, 14, 2, 'accepted'),
(22, 14, 3, 'accepted'),
(22, 14, 4, 'accepted'),
(22, 14, 5, 'accepted'),
(22, 14, 6, 'accepted'),
(22, 14, 7, 'accepted'),
(22, 14, 8, 'accepted'),
(22, 14, 9, 'accepted'),
(22, 14, 10, 'accepted'),
(22, 14, 11, 'accepted'),
(22, 14, 12, 'accepted'),
(22, 14, 13, 'accepted'),
(22, 14, 14, 'accepted'),
(22, 14, 15, 'accepted'),
(22, 14, 16, 'accepted');