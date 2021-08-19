--add operational territories for seed users pro@modobio.com and name@modobio.com

delete from "StaffOperationalTerritories" 
			where idx >= 1;
alter sequence "StaffOperationalTerritories_idx_seq"
  restart with 1;


insert into "StaffOperationalTerritories" ("user_id", "operational_territory_id", "role_id") values
(10,1,10),
(10,2,10),
(10,3,10),
(10,4,10),
(14,1,11),
(14,2,11),
(14,3,11),
(14,4,11);