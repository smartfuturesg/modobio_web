delete from "LookupSubscriptions" 
			where sub_id >= 1;
alter sequence "LookupSubscriptions_sub_id_seq"
  restart with 1;

INSERT INTO "LookupSubscriptions" ("name", "description", "cost", "frequency") 
VALUES
('Unsubscribed', 'Join a clinical care team!', 0.00, 'Monthly'),
('Wellness Plan', 'Make Telehealth Appointments\nHave Activity Tracker Data Analysed\nCreate a Clinical Care Team', 10.00, 'Monthly');