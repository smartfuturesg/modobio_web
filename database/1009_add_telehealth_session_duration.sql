delete from "LookupTelehealthSessionDuration" 
			where idx >= 1;
alter sequence "LookupTelehealthSessionDuration_idx_seq"
  restart with 1;

INSERT INTO "LookupTelehealthSessionDuration" ("session_duration") 
VALUES
(10),
(15),
(20),
(25),
(30),
(35),
(40),
(45),
(50),
(55),
(60);