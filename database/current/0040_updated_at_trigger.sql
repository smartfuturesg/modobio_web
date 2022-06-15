----------------------------------------------------------
-- Trigger function for updated_at column 
----------------------------------------------------------
CREATE OR REPLACE function refresh_updated_at() 
RETURNS trigger 
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := clock_timestamp();
  return NEW;
END;
$$;

----------------------------------------------------------
-- Sets refresh_updated_at trigger to all existing tables 
-- in the database that has the updated_at column 
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

----------------------------------------------------------
-- event trigger function that loops over any tables that 
-- doesn't have an updated_at_trigger and creates the 
-- update_at_trigger for it
----------------------------------------------------------
CREATE function create_trigger_after_create_event() 
RETURNS event_trigger  AS $event$
BEGIN
    do $$
    DECLARE
        r record;
	    BEGIN
	        FOR r IN 
	            SELECT * from information_schema."columns" c
                WHERE c.column_name = 'updated_at' AND NOT EXISTS
                    (SELECT * from information_schema.triggers t 
                    WHERE c.table_name = t.event_object_table AND t.trigger_name = 'updated_at_trigger')
	        LOOP
	            EXECUTE format('CREATE TRIGGER updated_at_trigger
	                            BEFORE UPDATE ON %I.%I
	                            FOR EACH ROW EXECUTE PROCEDURE %I.refresh_updated_at()',
	                            r.table_schema, r.table_name, r.table_schema);
	        END LOOP;
	    END; $$ LANGUAGE plpgsql;
	END;
$event$ 
LANGUAGE plpgsql;

----------------------------------------------------------
-- event trigger that calls create_trigger_after_create_event
-- after a new table has been added to the database
----------------------------------------------------------
CREATE EVENT TRIGGER updated_at_event_trigger_for_after_create 
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE PROCEDURE create_trigger_after_create_event();