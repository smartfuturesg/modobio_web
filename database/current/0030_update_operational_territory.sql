--remove territories from StaffOperationalTerritories
DELETE FROM "StaffOperationalTerritories" WHERE "operational_territory_id" IN (1, 3, 4);

---Below code about 'session_replication_role' no longer necessary
--May have been caused by order or script operation causing idx values here to
--become invalid foreign keys in the StaffOperationalTerritories table 

--temporarily suspend constaints while updating foreign keys
--SET session_replication_role = 'replica';

--delete all territories except for Florida, then change Florida's idx to 1 and restart sequence
DELETE FROM "LookupTerritoriesOfOperations" WHERE "idx" IN (1, 3, 4);
UPDATE "LookupTerritoriesOfOperations" SET "idx" = 1 WHERE "idx" = 2;
ALTER SEQUENCE "LookupTerritoriesOfOperations_idx_seq"
  restart with 2;
  
--restore constraints
--SET session_replication_role = 'origin';