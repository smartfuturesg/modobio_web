--remove territories from StaffOperationalTerritories
DELETE FROM "StaffOperationalTerritories" WHERE "operational_territory_id" IN (1, 3, 4);

--delete all territories except for Florida, then change Florida's idx to 1 and restart sequence
DELETE FROM "LookupTerritoriesOfOperations" WHERE "idx" IN (1, 3, 4);
UPDATE "LookupTerritoriesOfOperations" SET "idx" = 1 WHERE "idx" = 2;
ALTER SEQUENCE "LookupTerritoriesOfOperations_idx_seq"
  restart with 2;