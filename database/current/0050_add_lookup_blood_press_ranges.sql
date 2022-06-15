-----------------------------
-- Empty table and reset index. 
-- Rather than altering the table, this script inserts data 
-- So to avoid duplicates, we empty the table and reindex.
-- This is a solution that should be run only once on 
-- persistent databases. 
-- Further changes to this table will be done through the API
-----------------------------

DELETE FROM "LookupBloodPressureRanges"
    WHERE idx >= 1;

ALTER SEQUENCE "LookupBloodPressureRanges_idx_seq"
		RESTART WITH 1;

INSERT INTO "LookupBloodPressureRanges" ("category","systolic", "and_or","diastolic") 
VALUES 
('normal','less than 120','and','less than 80'),
('elevated','120-129','and','less than 80'),
('high blood pressure (hypertension) stage 1','130-139','or','80-90'),
('high blood pressure (hypertension) stage 2','140 or higher','or','90 or higher'),
('hypertensive crisis','higher than 180','and/or','higher than 120');