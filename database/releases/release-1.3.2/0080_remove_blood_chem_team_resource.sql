--NRV-3996 remove blood glucose from phr permissions (LookupClinicalCareTeamResources)

DELETE FROM "ClientClinicalCareTeamAuthorizations" 
WHERE resource_id IN (SELECT resource_id FROM "LookupClinicalCareTeamResources" where resource_name = 'blood_glucose');

DELETE FROM "LookupClinicalCareTeamResources" where resource_name = 'blood_glucose'