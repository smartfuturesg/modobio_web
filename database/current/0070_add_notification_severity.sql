delete from "LookupNotificationSeverity" 
			where idx >= 1;
alter sequence "LookupNotificationSeverity_idx_seq"
  restart with 1;

INSERT INTO "LookupNotificationSeverity" ("severity", "color") 
VALUES
('Highest','#FF0000'),
('High','#FF9400'),
('Medium','#FFC300'),
('Low','#1DB3FF'),
('Lowest','#00C5C5');