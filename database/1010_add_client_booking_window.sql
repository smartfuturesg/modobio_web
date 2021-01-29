delete from "LookupClientBookingWindow" 
			where idx >= 1;
alter sequence "LookupClientBookingWindow_idx_seq"
  restart with 1;

INSERT INTO "LookupClientBookingWindow" ("booking_window") 
VALUES
(8),
(9),
(10),
(11),
(12),
(13),
(14),
(15),
(16),
(17),
(18),
(19),
(20),
(21),
(22),
(23),
(24);