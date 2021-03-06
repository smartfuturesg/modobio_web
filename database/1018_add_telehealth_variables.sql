delete from "SystemVariables" 
			where var_id >= 1;
alter sequence "SystemVariables_var_id_seq"
  restart with 1;

INSERT INTO "SystemVariables" ("var_name","var_value") 
VALUES
('Session Duration', '30'),
('Booking Notice Window', '8'),
('Confirmation Window', '8.0');