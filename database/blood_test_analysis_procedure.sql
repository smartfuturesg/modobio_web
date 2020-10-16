---------------------------------------------------------------------------------------------------
-- Apply an auto amtic interpretation of blood test results 
-- Based optimal and normal ranges for test results from
-- American Board of Internal Medicine: 
-- Labratory Test Reference Ranges
-- rev. January 2020
---------------------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.blood_test_assessment(test_type text, test_value float)
 RETURNS varchar
 LANGUAGE plpgsql
AS $function$
declare
  assessment varchar;
  query varchar;
begin
  query := 'SELECT 
				CASE
					when '||test_value||' between optimal_min and optimal_max then ''optimal''
					when ' || test_value || ' >= optimal_min and optimal_max is null then ''optimal''
					when ' || test_value || ' <= optimal_max and optimal_min is null then ''optimal''
					when ' || test_value || ' between normal_min  and normal_max then ''normal''
					when ' || test_value || ' >= normal_min  and normal_max is null then ''normal''
					when ' || test_value || ' <= normal_max  and normal_min is null then ''normal''
					else ''abnormal''
				end as assessment
			from "MedicalBloodTestResultTypes" rt
			where rt.result_name =' || quote_nullable(test_type) || '';
  execute query into assessment;
  return assessment;
end;
$function$
;
;