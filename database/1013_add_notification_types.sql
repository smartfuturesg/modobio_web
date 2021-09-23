delete from "LookupNotifications" 
			where notification_type_id >= 1;
alter sequence "LookupNotifications_notification_type_id_seq"
  restart with 1;

INSERT INTO "LookupNotifications" ("notification_type","icon","background_color","symbol_color") 
VALUES
('Account Management', 'person.svg', 'gray', 'white'),
('System', 'build.svg', 'orange', 'white'),
('Scheduling', 'clock.svg', 'navy', 'white'),
('Action Required', 'siren.svg', 'white', 'original'),
('Payments', 'money.svg', 'green', 'white'),
('Profile', 'client-profile.svg', 'white', 'black'),
('Client Services', 'client-services.svg', 'white', 'green'),
('Medical', 'doctor.svg', 'white', 'red'),
('Nutrition', 'nutritionist.svg', 'white', 'orange'),
('Training', 'physical-training.svg', 'white', 'purple'),
('Physiotherapy', 'physiotherapy.svg', 'white', 'lightBlue'),
('Data Science', 'analytics.svg', 'white', 'navy'),
('Community', 'people.svg', 'pink', 'red'),
('Clinical Care Team', 'family.svg', 'white', 'pink'),
('Staff Administration', 'social-history.svg', 'black', 'white'),
('System Administration', 'setting.svg', 'black', 'white'),
('DoseSpot Notifications', 'doctor.svg', 'black', 'white');