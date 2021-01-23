CREATE OR REPLACE FUNCTION update_modified_column() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = clock_timestamp();
    RETURN NEW; 
END;
$$ language 'plpgsql';



DROP TRIGGER IF EXISTS update_lookup_created_at
  ON "LookupClinicalCareTeamResources";
CREATE TRIGGER update_lookup_created_at BEFORE UPDATE ON "LookupClinicalCareTeamResources"
     FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
