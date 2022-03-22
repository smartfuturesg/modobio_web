-- Fix the subcategory of closed fractions.
-- NRV-1155 was fixed in MEDICAL_CONDITIONS (constants.py) but copied wrong.

UPDATE "MedicalConditions"
    SET subcategory = 'History of fractures'
    WHERE category = 'Musculoskeletal' AND condition = 'Closed';
