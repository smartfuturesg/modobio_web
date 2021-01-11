delete from "LookupRaces" 
			where race_id >= 1;
alter sequence "LookupRaces_race_id_seq"
  restart with 1;

INSERT INTO "LookupRaces" ("race_name", "race_id") 
VALUES
('White / Caucasian', 1),
('Black / African American', 2),
('Native American / Alaska Native', 3),
('Asian', 4),
('Pacific Islander / Native Hawaiian', 5),
('Hispanic / Latino', 6);