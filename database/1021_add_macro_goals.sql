delete from "LookupMacroGoals" 
			where goal_id >= 1;
alter sequence "LookupMacroGoals_goal_id_seq"
  restart with 1;

INSERT INTO "LookupMacroGoals" ("goal_id","goal") 
VALUES
(1, 'Gain the best understanding I can of my health at any point in time.'),
(2, 'Work with my existing provider using the Modo Bio platform.'),
(3, 'Better understand how to achieve my own health goals.'),
(4, 'Track the state of a particular health condition or worry.'),
(5, 'Have someone to talk to about issues that may concern me from time to time.'),
(6, 'Other')