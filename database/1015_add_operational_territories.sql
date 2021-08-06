delete from "LookupTerritoriesofOperation" 
			where idx >= 1;
alter sequence "LookupTerritoriesofOperation_idx_seq"
  restart with 1;

delete from "LookupCountriesofOperation" 
			where idx >= 1;
alter sequence "LookupCountriesOfOperation_idx_seq"
  restart with 1;

INSERT INTO "LookupCountriesOfOperation" ("country")
VALUES
('USA');

INSERT INTO "LookupTerritoriesofOperation" ("country_id", "sub_territory", "sub_territory_abbreviation") 
VALUES
(1, 'Alabama', 'AL'),
(1, 'Arizona', 'AZ'),
(1, 'Colorado', 'CO'),
(1, 'Georgia', 'GA'),
(1, 'Iowa', 'IA'),
(1, 'Idaho', 'ID'),
(1, 'Illinois', 'IL'),
(1, 'Kansas', 'KS'),
(1, 'Kentucky', 'KY'),
(1, 'Maryland', 'MD'),
(1, 'Maine', 'ME'),
(1, 'Michigan', 'MI'),
(1, 'Minnesota', 'MN'),
(1, 'Montana', 'MT'),
(1, 'Mississippi', 'MS'),
(1, 'North Dakota', 'ND'),
(1, 'Nebraska', 'NE'),
(1, 'New Hampshire', 'NH'),
(1, 'New Jersey', 'NJ'), 
(1, 'Nevada', 'NV'), 
(1, 'Oklahoma', 'OK'),
(1, 'South Dakota', 'SD'),
(1, 'Tennessee', 'TN'),
(1, 'Utah', 'UT'), 
(1, 'Vermont', 'VT'),
(1, 'Washington', 'WA'),
(1, 'Wisconsin', 'WI'),
(1, 'West Virginia', 'WV'),
(1, 'Wyoming', 'WY')