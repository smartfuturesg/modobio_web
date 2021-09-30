delete from "LookupSubscriptions" 
			where sub_id >= 1;
alter sequence "LookupSubscriptions_sub_id_seq"
  restart with 1;

INSERT INTO "LookupSubscriptions" ("name", "description", "cost", "frequency") 
VALUES
('Monthly', 'Make Telehealth Appointments.\nStore and control who sees your health data.\nConnect a supported activity tracker.\nCreate a team of health professionals, family, and friends.', 9.99, 'Monthly'),
('Annual', 'All of the above but pay for 10 months and get 2 free.', 98.00, 'Annually');