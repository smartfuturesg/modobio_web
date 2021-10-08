delete from "LookupCurrencies"
  where idx >= 1;
alter sequence "LookupCurrencies_idx_seq"
  restart with 1;

INSERT INTO "LookupCurrencies" ("country", "symbol_and_code","min_rate","max_rate","increment")
VALUES
('USA', '$ / USD',30,500,5);