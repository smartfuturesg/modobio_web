-- Updates LookupNotifications table as per NRV-2726
UPDATE "LookupNotifications"
SET "notification_type" = 'Account', "icon" = 'Account.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 1;

UPDATE "LookupNotifications"
SET "notification_type" = 'System Maintenance', "icon" = 'SystemMaintenance.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 2;

UPDATE "LookupNotifications"
SET "icon" = 'Calendar.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 3;

UPDATE "LookupNotifications"
SET "icon" = 'ActionRequired.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 4;

UPDATE "LookupNotifications"
SET "icon" = 'Payments.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 5;

UPDATE "LookupNotifications"
SET "icon" = 'Identity.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 6;

UPDATE "LookupNotifications"
SET "icon" = 'ClientsServices.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 7;

UPDATE "LookupNotifications"
SET "notification_type" = 'Medical Doctor', "icon" = 'MedicalDoctor.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 8;

UPDATE "LookupNotifications"
SET "notification_type" = 'Dietitian', "icon" = 'Dietitian.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 9;

UPDATE "LookupNotifications"
SET "notification_type" = 'Trainer', "icon" = 'Trainer.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 10;

UPDATE "LookupNotifications"
SET "notification_type" = 'Physical Therapist', "icon" = 'PhysicalTherapist.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 11;

UPDATE "LookupNotifications"
SET "icon" = 'Analytics.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 12;

UPDATE "LookupNotifications"
SET "icon" = 'Community.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 13;

UPDATE "LookupNotifications"
SET "notification_type" = 'Team', "icon" = 'Dock Team.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 14;

UPDATE "LookupNotifications"
SET "notification_type" = 'Staff', "icon" = 'Staff.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 15;

UPDATE "LookupNotifications"
SET "icon" = 'System Admin.svg', "updated_at" = CURRENT_TIMESTAMP 
WHERE "notification_type_id" = 16;

INSERT INTO "LookupNotifications"
VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 18, 'Chef', 'Chef.svg');

INSERT INTO "LookupNotifications"
VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 19, 'Therapist', 'Therapist.svg');

INSERT INTO "LookupNotifications"
VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 20, 'Health', 'Dock Health.svg');