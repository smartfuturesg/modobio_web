delete from "SystemTelehealthSessionCosts" 
			where cost_id >= 1;
alter sequence "SystemTelehealthSessionCosts_cost_id_seq"
  restart with 1;

INSERT INTO "SystemTelehealthSessionCosts" ("profession_type","country","session_cost","session_min_cost","session_max_cost") 
VALUES
('doctor', 'USA', 100.00, 50.00, 200.00),
('nutrition', 'USA', 100.00, 50.00, 200.00),
('physical_therapist', 'USA', 100.00, 50.00, 200.00),
('trainer', 'USA', 100.00, 50.00, 200.00);
