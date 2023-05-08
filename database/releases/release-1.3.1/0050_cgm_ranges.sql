
insert into "LookupCGMDemographics" ("demographic", "display_name")
values ('diabetes_1_2', 'Type 1 & Type 2 Diabetes'),
        ('high_risk_older_diabetes_1_2', 'Older/High-Risk Type 1 & Type 2 Diabetes'),
        ('pregnant_diabetes_1', 'Pregnancy Type 1 Diabetes'),
        ('pregnant_gestational_diabetes_2', 'Pregnancy Gestational & Type 2 Diabetes');


insert into "LookupBloodGlucoseCGMRanges" ("demographic_id", "classification", "min_mg_dL", "max_mg_dL", "min_mmol_L", "max_mmol_L", "min_percent_in", "max_percent_in", "min_time_in", "max_time_in")
values (1, 'Very High', 250, null, 13.9,null, 0, 5, 0, 72 ),
        (1, 'High', 180, 250, 10, 13.9, 0, 25 ,0, 360),
        (1, 'Target', 70, 180, 3.9, 10, 70, 100, 1008, 1440),
        (1, 'Low', 54, 70, 3, 3.9, 0, 4, 0, 57.6),
        (1, 'Very Low', 0, 54, 0, 3, 0, 1, 0, 14.4 ),
        (2, 'Very High', 250, null, 13.9, null, 0, 10, 0, 144),
        (2, 'High', 180, 250, 10, 13.9, 0, 50, 0, 720),
        (2, 'Target', 70, 180, 3.9, 10, 50, 100, 720, 1440),
        (2, 'Low', 0, 70, 0, 3.9, 0, 1, 0, 14.4),
        (3, 'High', 140, null, 7.8, null, 0, 25, 0, 360),
        (3, 'Target', 63, 140, 3.5, 7.8, 70, 100, 1008, 1440),
        (3, 'Low', 54, 63, 3, 3.5, 0, 4, 0, 57.6),
        (3, 'Very Low', 0, 54, 0,3, 0, 1, 0, 14.4),
        (4, 'High', 140, null, 7.8, null, null, null, null, null),
        (4, 'Target', 63, 140, 3.5, 7.8, null, null, null, null),
        (4, 'Low', 54, 63, 3, 3.5, null, null, null, null),
        (4, 'Very Low', 0, 54, 0, 3, null, null, null, null);