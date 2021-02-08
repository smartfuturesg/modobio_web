delete from "LookupTelehealthSessionCost" 
			where idx >= 1;
alter sequence "LookupTelehealthSessionCost_idx_seq"
  restart with 1;

INSERT INTO "LookupTelehealthSessionCost" ("profession_type","territory","session_cost") 
VALUES
('Medical Doctor', 'USA', 200),
('Medical Doctor', 'UK', 200);