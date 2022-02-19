-- Updated desciption and frequency of monthly and anual subscription plans

UPDATE "LookupSubscriptions"
    set description = 'Make Telehealth Appointments.\nStore and control who sees your health data.\nConnect a supported activity tracker.\nCreate a team of health providers, family, and friends.',
        frequency = 'Month',
        ios_product_id = 'MB_Monthly_ARS_9.99_01'
    where name = 'Monthly'; 


UPDATE "LookupSubscriptions"
    set frequency = 'Year',
        ios_product_id = 'MB_Annual_ARS_97.99_01'
    where name = 'Annual'; 