ALTER TABLE "LookupCurrencies"
ADD COLUMN "min_rate" Float,
ADD COLUMN "max_rate" Float,
ADD COLUMN "increment" Integer;

UPDATE "LookupCurrencies"
SET min_rate = 30.00
WHERE idx = 1;

UPDATE "LookupCurrencies"
SET max_rate = 500.00
WHERE idx = 1;

UPDATE "LookupCurrencies"
SET increment = 5
WHERE idx = 1;

