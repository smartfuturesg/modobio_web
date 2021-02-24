delete from "LookupTelehealthSessionCost" 
			where idx >= 1;
alter sequence "LookupTelehealthSessionCost_idx_seq"
  restart with 1;

INSERT INTO "LookupTelehealthSessionCost" ("profession_type","territory","session_min_cost","session_max_cost") 
VALUES
('Medical Doctor', 'USA', 50.00, 200.00),
('Medical Doctor', 'UK', 50.00, 200.00);