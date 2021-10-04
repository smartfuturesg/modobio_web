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

delete from "SystemTelehealthSessionCosts" 
			where cost_id >= 1;
alter sequence "SystemTelehealthSessionCosts_cost_id_seq"
  restart with 1;

delete from "LookupCurrencies"
  where idx >= 1;
alter sequence "LookupCurrencies_idx_seq"
  restart with 1;

INSERT INTO "LookupCurrencies" ("country", "symbol_and_code","min_rate","max_rate","increment")
VALUES
('USA', '$ / USD',30,500,5);

delete from "SystemTelehealthSessionCosts"
  where cost_id >= 1;
alter sequence "SystemTelehealthSessionCosts_cost_id_seq"
  restart with 1;

INSERT INTO "SystemTelehealthSessionCosts" ("currency_id", "profession_type","session_cost","session_min_cost","session_max_cost") 
VALUES
(1, 'medical_doctor', 100.00, 60.00, 200.00),
(1, 'nutritionist', 100.00, 60.00, 200.00),
(1, 'physical_therapist', 100.00, 60.00, 200.00),
(1, 'trainer', 100.00, 60.00, 200.00);

delete from "LookupProfessionalAppointmentConfirmationWindow" 
			where idx >= 1;
alter sequence "LookupProfessionalAppointmentConfirmationWindow_idx_seq"
  restart with 1;

INSERT INTO "LookupProfessionalAppointmentConfirmationWindow" ("confirmation_window") 
VALUES
(1.0),
(1.5),
(2.0),
(2.5),
(3.0),
(3.5),
(4.0),
(4.5),
(5.0),
(5.5),
(6.0),
(6.5),
(7.0),
(7.5),
(8.0),
(8.5),
(9.0),
(9.5),
(10.0),
(10.5),
(11.0),
(11.5),
(12.0),
(12.5),
(13.0),
(13.5),
(14.0),
(14.5),
(15.0),
(15.5),
(16.0),
(16.5),
(17.0),
(17.5),
(18.0),
(18.5),
(19.0),
(19.5),
(20.0),
(20.5),
(21.0),
(21.5),
(22.0),
(22.5),
(23.0),
(23.5),
(24.0);

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

delete from "SystemVariables" 
			where var_id >= 1;
alter sequence "SystemVariables_var_id_seq"
  restart with 1;

INSERT INTO "SystemVariables" ("var_name","var_value") 
VALUES
('Session Duration', '30'),
('Booking Notice Window', '8'),
('Confirmation Window', '8.0');