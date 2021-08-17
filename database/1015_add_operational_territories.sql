delete from "LookupTerritoriesOfOperations" 
			where idx >= 1;
alter sequence "LookupTerritoriesOfOperations_idx_seq"
  restart with 1;

delete from "LookupCountriesOfOperations" 
			where idx >= 1;
alter sequence "LookupCountriesOfOperations_idx_seq"
  restart with 1;

INSERT INTO "LookupCountriesOfOperations" ("country")
VALUES
('USA');

INSERT INTO "LookupTerritoriesOfOperations" ("country_id", "sub_territory", "sub_territory_abbreviation") 
VALUES
(1, 'California', 'CA'),
(1, 'Florida', 'FL'),
(1, 'New York', 'NY'),
(1, 'Texas', 'TX');