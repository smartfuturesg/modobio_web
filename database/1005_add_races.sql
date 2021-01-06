DO $$
DECLARE
  x integer;
  query varchar := 'select count(*) from "LookupRaces"';
BEGIN 
execute query into x;
  IF x >= 1 THEN
   execute 
   		'delete from "LookupRaces" 
			where idx >= 1;
		alter sequence "LookupRaces_idx_seq"
			restart with 1;';
  END IF;

INSERT INTO "LookupRaces" ("race_name", "race_id") 
VALUES
('White / Caucasian', 1),
('Black / African American', 2),
('Native American / Alaska Native', 3),
('Asian', 4),
('Pacific Islander / Native Hawaiian', 5),
('Hispanic / Latino', 6);