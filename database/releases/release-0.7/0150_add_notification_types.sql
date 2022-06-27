delete from "LookupNotifications" 
			where notification_type_id >= 1;
alter sequence "LookupNotifications_notification_type_id_seq"
  restart with 1;

INSERT INTO "LookupNotifications" ("notification_type","icon") 
VALUES
('Account Management', 'person.svg'),
('System', 'build.svg'),
('Scheduling', 'clock.svg'),
('Action Required', 'siren.svg'),
('Payments', 'money.svg'),
('Profile', 'client-profile.svg'),
('Client Services', 'client-services.svg'),
('Medical', 'doctor.svg'),
('Nutrition', 'nutritionist.svg'),
('Training', 'physical-training.svg'),
('Physiotherapy', 'physiotherapy.svg'),
('Data Science', 'analytics.svg'),
('Community', 'people.svg'),
('Clinical Care Team', 'family.svg'),
('Staff Administration', 'social-history.svg'),
('System Administration', 'setting.svg'),
('DoseSpot', 'doctor.svg');