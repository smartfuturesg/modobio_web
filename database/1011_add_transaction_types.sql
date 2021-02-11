delete from "LookupTransactionTypes" 
			where idx >= 1;
alter sequence "LookupTransactionTypes_idx_seq"
  restart with 1;

INSERT INTO "LookupTransactionTypes" ("category","name","icon") 
VALUES
('Telehealth', 'Medical', 'doctor.svg'),
('Subscription', 'Wellness Plan', 'history.svg'),
('Product', 'Supplements', 'supplementations.svg');