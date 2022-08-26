UPDATE "LookupTerritoriesOfOperations"
	SET active=false
	WHERE idx=1;
UPDATE "LookupTerritoriesOfOperations"
	SET active=true
	WHERE idx=4;