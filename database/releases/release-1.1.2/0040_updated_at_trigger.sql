----------------------------------------------------------
-- Trigger function for updated_at column
--
-- This function sets the 'updated_at' column to
-- the current timestamp on update of the row.
----------------------------------------------------------
CREATE OR REPLACE FUNCTION refresh_updated_at()
RETURNS trigger
AS $$
BEGIN
    -- NEW is an automatically created variable (type record)
    -- that holds the new database row after update.
    NEW.updated_at := clock_timestamp();
    return NEW;
END;
$$ LANGUAGE plpgsql;

----------------------------------------------------------
-- This PL/PGSQL code is called when this script is executed,
-- i.e. when the database/sql_scriptrunner.py' script is run.
--
-- It loops over all tables in the 'public' schema that have
-- an 'updated_at' column. It attaches a trigger to the
-- updated_at column that calls the refresh_updated_at function.
----------------------------------------------------------
DO $$
DECLARE
    t record;
BEGIN
    FOR t IN 
        SELECT * FROM information_schema.columns
        WHERE column_name = 'updated_at' AND table_schema = 'public'
    LOOP
        EXECUTE format(
            'CREATE OR REPLACE TRIGGER updated_at_trigger
            BEFORE UPDATE ON public.%I
            FOR EACH ROW EXECUTE FUNCTION public.refresh_updated_at()',
            t.table_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

----------------------------------------------------------
-- The above code section only acts on already existing tables.
-- Since this code is run only once in production, it does not
-- include tables that will be created in the future.
--
-- This function will be called from an event trigger. Event
-- triggers fire on DDL events, in this case CREATE TABLE.
-- When called, this function adds the refresh_updated_at()
-- trigger to the newly created table, if it is in the 'public'
-- schema and has a 'updated_at' column.
----------------------------------------------------------
CREATE OR REPLACE FUNCTION add_updated_at_trigger_to_new_table()
RETURNS event_trigger
AS $$
DECLARE
    r record;
BEGIN
    -- Only add if table has a updated_at column. Column names of the
    -- created table are not available from pg_event_trigger_ddl_commands,
    -- but luckily this function is called AFTER table creation (ddl_command_end
    -- in the CREATE EVENT TRIGGER) so it's in the information_schema table.
    FOR r IN
        SELECT * FROM pg_event_trigger_ddl_commands() AS pg
        WHERE pg.object_type = 'table'
        AND pg.schema_name = 'public'
        AND 'updated_at' IN (
            SELECT column_name FROM information_schema.columns
            WHERE ARRAY[table_schema, table_name]::text[] = parse_ident(pg.object_identity))
    LOOP
        EXECUTE format(
            'CREATE OR REPLACE TRIGGER updated_at_trigger
            BEFORE UPDATE ON %s
            FOR EACH ROW EXECUTE FUNCTION public.refresh_updated_at()',
            r.object_identity);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

----------------------------------------------------------
-- Create an event trigger that calls add_updated_at_trigger_to_new_table()
-- when a new table is created.
-- Event triggers don't have CREATE OR REPLACE, so delete old first.
----------------------------------------------------------
DROP EVENT TRIGGER IF EXISTS add_updated_at_trigger_to_new_table_event_trigger;
CREATE EVENT TRIGGER add_updated_at_trigger_to_new_table_event_trigger
    ON ddl_command_end
    WHEN TAG IN ('CREATE TABLE')
    EXECUTE FUNCTION add_updated_at_trigger_to_new_table();

-- Drop old names
DROP EVENT TRIGGER IF EXISTS updated_at_event_trigger_for_after_create;
DROP FUNCTION IF EXISTS create_trigger_after_create_event;
