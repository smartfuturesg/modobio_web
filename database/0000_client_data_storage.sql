-------------------
-- This script creates the necessary functions and views to estimate how much data is 
-- currently stored for each client. THis takes in to account full relations (tables, index, TOAST, relations)
-------------------

---------------------------------------------------------------------------------------------------
-- row_counter
-- number of rows per the specified table 
---------------------------------------------------------------------------------------------------
create or replace function 
row_counter(schema text, tablename text) returns integer
as
$body$
declare
  result integer;
  query varchar;
begin
  query := 'SELECT count(1) FROM ' || schema || '.' || tablename;
  execute query into result;
  return result;
end;
$body$
language plpgsql;;
---------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------

---------------------------------------------------------------------------------------------------
-- client_entries_per_table
-- number of rows per specified table anduser_id
---------------------------------------------------------------------------------------------------
create or replace function 
client_entries_per_table(schema text, tablename text, user_id integer ) returns integer
as
$body$
declare
  result integer;
  query varchar;
begin
  query := 'SELECT count(1) FROM ' || schema || '.' || tablename || 'where user_id =' || user_id ;
  execute query into result;
  return result;
end;
$body$
language plpgsql;;
;
;
---------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------

---------------------------------------------------------------------------------------------------
-- client_medical_images_total_bytes
-- total byte size of medical images stored for specified user_id 
---------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.client_medical_images_total_bytes(user_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
declare
  result integer;
  query varchar;
begin
  query := 'SELECT SUM(image_size) FROM public."MedicalImaging" ' || 'where user_id =' || user_id || 'GROUP BY user_id';
  execute query into result;
  return coalesce(result, 0);
end;
$function$
;

---------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------


---------------------------------------------------------------------------------------------------
-- client_table_sizes
-- Size and average row size in bytes of all public tables which hold client data referenced by user_id 
---------------------------------------------------------------------------------------------------
create or replace view public.client_table_sizes 
as
select t.table_schema, 
		t.table_name, 
		pg_total_relation_size('"'||t.table_schema||'"."'||t.table_name||'"') as total_size,
		public.row_counter(t.table_schema, '"'||t.table_name||'"') as row_count,
	case 
		when public.row_counter(t.table_schema, '"'||t.table_name||'"') > 0
			then pg_total_relation_size('"'||t.table_schema||'"."'||t.table_name||'"') / public.row_counter(t.table_schema, '"'||t.table_name||'"')
		else 0
	 end as bytes_per_row
from information_schema.tables as t
inner join information_schema.columns as c
	on t.table_name = c.table_name 
		and t.table_schema = c.table_schema 
where t.table_schema = 'public'
	and t.table_type = 'BASE TABLE'
	and (c.column_name = 'user_id');
---------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------

---------------------------------------------------------------------------------------------------
-- data_per_client
-- must be after running the script above, we ca
---------------------------------------------------------------------------------------------------
create or replace view public.data_per_client
as
select  user_id, 
		sum(client_entries_per_table(table_schema, '"'||table_name||'"', user_id) * bytes_per_row)
			+ client_medical_images_total_bytes(user_id) as total_bytes,
		case
			when sum(client_entries_per_table(table_schema, '"'||table_name||'"', user_id) * bytes_per_row)
				+ client_medical_images_total_bytes(user_id) < 10000000 
				then 'Tier 1'
			else 'Tier 2'
		end as data_usage_tier
from public.client_table_sizes
join "ClientInfo" on 1=1
group by user_id ;
---------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------