-- Updated wearable_data care team resouce display name

UPDATE "LookupClinicalCareTeamResources" 
	SET display_name = 'Data Dashboard'
WHERE resource_name = 'wearable_data'