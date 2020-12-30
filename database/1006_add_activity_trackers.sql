-----------------------------
-- Empty table and reset index. 
-- Rather than altering the table, this script inserts data 
-- So to avoid duplicates, we empty the table and reindex.
-- This is a solution that should be run only once on 
-- persistent databases. 
-- Further changes to this table will be done through the API
-----------------------------

DELETE FROM "LookupActivityTrackers"
    WHERE idx >= 1;

ALTER SEQUENCE "LookupActivityTrackers_idx_seq"
		RESTART WITH 1;

INSERT INTO "LookupActivityTrackers" ("brand","series", "model","ecg_metric_1",
                                      "ecg_metric_2", "sp_o2_spot_check", "sp_o2_nighttime_avg", "sleep_total",
                                      "deep_sleep", "rem_sleep", "quality_sleep", "light_sleep",
                                      "awake", "sleep_latency", "bedtime_consistency", "wake_consistency",
                                      "rhr_avg", "rhr_lowest", "hr_walking", "hr_24hr_avg",
                                      "hrv_avg", "hrv_highest", "respiratory_rate", "body_temperature",
                                      "steps", "total_calories", "active_calories", "walking_equivalency",
                                      "inactivity") 
VALUES 
('Apple','3',null,false,false,false,false,true,true,false,true,true,true,true,true,true,true,false,true,true,true,false,false,false,true,true,true,true,false),
('Apple','4',null,true,true,false,false,true,true,false,true,true,true,true,true,true,true,false,true,true,true,false,false,false,true,true,true,true,false),
('Apple','5',null,true,true,false,false,true,true,false,true,true,true,true,true,true,true,false,true,true,true,false,false,false,true,true,true,true,false),
('Apple','6',null,true,true,true,true,true,true,false,true,true,true,true,true,true,true,false,true,true,true,false,false,false,true,true,true,true,false),
('Apple','SE', null,false,false,false,false,true,true,false,true,true,true,true,true,true,true,false,true,true,true,false,false,false,true,true,true,true,false),
('Fitbit', 'Sense', null, true,false,false,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,true,true,true,false,true,false),
('Fitbit', 'Versa', '2',false,false,false,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,true,true,true,false,true,false),
('Fitbit', 'Versa', '3',false,false,false,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,true,true,true,false,true,false),
('Fitbit', 'Versa', 'Lite',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,false,true,false),
('Fitbit', 'Inspire', '2',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,false,true,false),
('Fitbit', 'Charge', '4',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,false,true,false),
('Samsung', 'Galaxy', '3',true,true,true,true,true,true,true,false,true,true,false,true,true,true,true,false,true,false,false,false,false,true,true,true,true,false),
('Samsung', 'Galaxy', 'Active',true,true,false,false,true,true,true,false,true,true,false,true,true,true,true,false,true,false,false,false,false,true,true,true,true,false),
('Samsung', 'Galaxy', 'Active 2',false,false,false,false,true,true,true,false,true,true,false,true,true,true,true,false,true,false,false,false,false,true,true,true,true,false),
('Samsung', 'Galaxy', 'Fit 2',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Samsung', 'Gear', 'Fit 2',false,false,false,false,true,false,false,false,true,false,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Samsung', 'Gear', 'S3',false,false,false,false,true,false,false,false,true,false,false,true,true,false,false,false,true,false,false,false,false,true,true,true,true,false),
('Garmin', 'Vivo', 'Vivoactive 4',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Vivo', 'Vivoactive 4s',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Vivo', 'Vivomove 3s', false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Vivo', 'Vivomove 3',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Vivo', 'Vivomove Style',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Vivo', 'Vivomove Lux',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Vivo', 'Vivosmart 4',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,false,false,true,true,true,true,false),
('Garmin', 'Vivo', 'Vivofit 4',false,false,false,false,true,true,true,false,true,true,false,true,true,false,false,false,false,false,false,false,false,true,true,true,true,false),
('Garmin', 'Forerunner', '745',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Forerunner', '945',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Forerunner', '245',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,false,false,true,true,true,true,false),
('Garmin', 'Forerunner', '245 Music',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,false,false,true,true,true,true,false),
('Garmin', 'Forerunner', '45',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Garmin', 'Forerunner', '45s',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Garmin', 'Forerunner', '35',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Garmin', 'Fenix', '6 Pro Solar',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Fenix', '6 Pro and Saphire',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Fenix', '6s Pro Solar',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Fenix', '6s Pro and Saphire',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Fenix', '6s',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Fenix', '6x Pro and Saphire',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Fenix', '6x Pro Solar',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Venu', 'Venu',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', 'Fenix', 'Venu Sq',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,true,false,true,false,true,true,true,true,false),
('Garmin', null, 'Instinct',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Garmin', null, 'Approach S62',false,false,true,true,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Garmin', null, 'Approach S60',false,false,false,false,true,true,true,false,true,true,false,true,true,false,false,false,false,false,false,false,false,true,true,true,true,false),
('Garmin', null, 'Approach S40',false,false,false,false,true,true,true,false,true,true,false,true,true,false,false,false,false,false,false,false,false,true,false,false,false,false),
('Oura', null, 'Ring',false,false,false,false,true,true,true,false,true,true,true,true,true,true,true,false,false,true,true,true,true,true,true,true,true,true),
('Whoop',null,null,false,false,false,false,true,true,true,false,true,true,true,true,true,true,false,false,true,true,false,true,false,false,true,false,false,false),
('Fossil',null,'Gen 5',false,false,false,false,true,false,false,false,true,false,false,true,true,true,false,false,true,false,false,false,false,true,true,false,true,false),
('Fossil',null,'Gen 4',false,false,false,false,true,false,false,false,true,false,false,true,true,true,false,false,true,false,false,false,false,true,true,false,true,false),
('Fossil',null,'Gen Sport',false,false,false,false,true,false,false,false,true,false,false,true,true,true,false,false,true,false,false,false,false,true,true,false,true,false),
('Suunto',null,'9',false,false,false,false,true,true,false,false,false,true,false,true,true,true,true,false,true,false,false,false,false,true,true,true,true,false),
('Suunto',null,'7',false,false,false,false,true,true,false,false,false,true,false,true,true,true,false,false,false,false,false,false,false,true,true,true,true,false),
('Suunto',null,'5',false,false,false,false,true,true,false,false,false,true,false,true,true,true,false,false,false,false,false,false,false,true,true,true,true,false),
('Polar',null,'Vantage V2',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Polar',null,'Vantage',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Polar',null,'Unite',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Polar',null,'A370',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Polar',null,'M430',false,false,false,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,true,true,true,false),
('Wyze',null,null,false,false,false,false,true,false,false,false,false,false,false,true,true,false,true,false,false,false,false,false,false,true,false,true,true,false),
('Honor Magic',null,'2',false,false,true,false,true,true,true,false,true,true,false,true,true,true,false,false,true,false,false,false,false,true,false,true,true,false),
('TicWatch',null,'Pro 3',false,false,true,true,true,true,true,false,true,true,true,true,true,true,true,false,true,false,false,false,false,true,true,false,true,false),
('Amazon',null,'Halo',false,false,false,false,true,true,true,false,true,true,true,true,true,false,false,false,true,false,false,false,false,true,true,false,false,true);










