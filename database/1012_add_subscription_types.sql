delete from "LookupSubscriptions" 
			where sub_id >= 1;
alter sequence "LookupSubscriptions_sub_id_seq"
  restart with 1;

INSERT INTO "LookupSubscriptions" ("name", "description", "cost", "frequency") 
VALUES
('Team Member', 'Join a team made by a family member, friend, or client.\nSee the health data other users share with you. ', 0.00, 'Monthly'),
('Monthly', 'Make Telehealth Appointments.\nStore and control who sees your health data.\nConnect a supported activity tracker.\nCreate a team of health professionals, family, and friends.', 9.99, 'Monthly'),
('Annual', 'All of the above but pay for 10 months and get 2 free.', 98.00, 'Annually');