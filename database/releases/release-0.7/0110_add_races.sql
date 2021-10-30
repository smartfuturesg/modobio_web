delete from "LookupRaces" 
			where race_id >= 1;
alter sequence "LookupRaces_race_id_seq"
  restart with 1;

INSERT INTO "LookupRaces" ("race_name") 
VALUES
('Unknown'),
('White, Caucasian'),
('Middle Eastern'),
('Black, African American'),
('Native American'),
('Alaska Native'),
('Asian'),
('Pacific Islander'),
('Native Hawaiian'),
('Ashkenazi Jewish'),
('Hispanic'),
('Latino');