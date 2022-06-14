----------------------------------------------------------
-- Trigger function for updated_at column 
----------------------------------------------------------
CREATE OR REPLACE function refresh_updated_at() 
RETURNS trigger 
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now();
  return NEW;
END;
$$;

----------------------------------------------------------
-- Sets refresh_updated_at trigger to all tables in the
-- database that has the updated_at column 
----------------------------------------------------------
DO $$
DECLARE
    t record;
BEGIN
    FOR t IN 
        SELECT * FROM information_schema.columns
        WHERE column_name = 'updated_at'
    LOOP
        EXECUTE format('CREATE TRIGGER updated_at_trigger
                        BEFORE UPDATE ON %I.%I
                        FOR EACH ROW EXECUTE PROCEDURE %I.refresh_updated_at()',
                        t.table_schema, t.table_name, t.table_schema);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
