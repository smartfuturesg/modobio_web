delete from "LookupClinicalCareTeamResources" where resource_name = 'medications';

insert into "LookupClinicalCareTeamResources" ("resource_name", "display_name", "access_group")
values ('fitness_goals', 'Fitness Goals', 'general');