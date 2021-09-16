--add operational territories for seed users pro@modobio.com and name@modobio.com 
--NOTE: StaffOperationalTerritories is obsolete, but will be kept in until we can safely remove it
--PractitionerCredentials will take its place, so it is also filled out here

delete from "StaffOperationalTerritories" 
			where idx >= 1;
alter sequence "StaffOperationalTerritories_idx_seq"
  restart with 1;
  
delete from "PractitionerCredentials" 
			where idx >= 1;
alter sequence "PractitionerCredentials_idx_seq"
  restart with 1;


insert into "StaffOperationalTerritories" ("user_id", "operational_territory_id", "role_id") values
(10,1,10),
(10,2,10),
(10,3,10),
(10,4,10),
(14,1,11),
(14,2,11),
(14,3,11),
(14,4,11),
(30, 1 ,75),
(30, 2 ,75),
(30, 3 ,75),
(30, 4 ,75),
(31, 1 ,76),
(31, 2 ,76),
(31, 3 ,76),
(31, 4 ,76),
(32, 1 ,77),
(32, 2 ,77),
(32, 3 ,77),
(32, 4 ,77),
(33, 1 ,78),
(33, 2 ,78),
(33, 3 ,78),
(33, 4 ,78);

insert into "PractitionerCredentials" ("user_id", "country_id", "state", "credential_type", "credentials", "status", "role_id", "want_to_practice") values
(10, 1, Null, 'npi', '1296336567', 'Verified', 13, True),
(10, 1, 'AZ', 'dea', '183451435', 'Verified', 13, True),
(10, 1, 'CA', 'dea', '123342534', 'Verified', 13, True),
(10, 1, 'AZ', 'med_lic', '523746512', 'Verified', 13, True),
(10, 1, 'CA', 'med_lic', '839547692', 'Verified', 13, True),
(14, 1, Null, 'npi', '1296336567', 'Verified', 13, True),
(14, 1, 'CA', 'dea', '43218470', 'Verified', 13, True),
(14, 1, 'AZ', 'med_lic', '21323512', 'Verified', 13, True);