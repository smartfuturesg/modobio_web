delete from "LookupTerritoriesofOperation" 
			where idx >= 1;
alter sequence "LookupTerritoriesofOperation_idx_seq"
  restart with 1;

INSERT INTO "LookupTerritoriesofOperation" ("country", "sub_territory", "sub_territory_abbreviation") 
VALUES
('USA', 'Alabama', 'AL'),
('USA', 'Arizona', 'AZ'),
('USA', 'Colorado', 'CO'),
('USA', 'Georgia', 'GA'),
('USA', 'Iowa', 'IA'),
('USA', 'Idaho', 'ID'),
('USA', 'Illinois', 'IL'),
('USA', 'Kansas', 'KS'),
('USA', 'Kentucky', 'KY'),
('USA', 'Maryland', 'MD'),
('USA', 'Maine', 'ME'),
('USA', 'Michigan', 'MI'),
('USA', 'Minnesota', 'MN'),
('USA', 'Montana', 'MT'),
('USA', 'Mississippi', 'MS'),
('USA', 'North Dakota', 'ND'),
('USA', 'Nebraska', 'NE'),
('USA', 'New Hampshire', 'NH'),
('USA', 'New Jersey', 'NJ'), 
('USA', 'Nevada', 'NV'), 
('USA', 'Oklahoma', 'OK'),
('USA', 'South Dakota', 'SD'),
('USA', 'Tennessee', 'TN'),
('USA', 'Utah', 'UT'), 
('USA', 'Vermont', 'VT'),
('USA', 'Washinton', 'WA'),
('USA', 'Wisconsin', 'WI'),
('USA', 'West Virginia', 'WV'),
('USA', 'Wyoming', 'WY')