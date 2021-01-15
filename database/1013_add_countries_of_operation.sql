delete from "LookupCountriesOfOperations" 
			where idx >= 1;
alter sequence "LookupCountriesOfOperations_idx_seq"
  restart with 1;

INSERT INTO "LookupCountriesOfOperations" ("country") 
VALUES
('United States (USA)');