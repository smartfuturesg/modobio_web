delete from "LookupUSStates" 
			where idx >= 1;
alter sequence "LookupUSStates_idx_seq"
  restart with 1;

INSERT INTO "LookupUSStates" ("abbreviation", "state", "territory_id") 
VALUES
('AL','Alabama',NULL),
('AK','Alaska',NULL),
('AZ','Arizona',NULL),
('AR','Arkansas',NULL),
('CA','California',NULL),
('CO','Colorado',NULL),
('CT','Connecticut',NULL),
('DE','Delaware',NULL),
('FL','Florida',1),
('GA','Georgia',NULL),
('HI','Hawaii',NULL),
('ID','Idaho',NULL),
('IL','Illinois',NULL),
('IN','Indiana',NULL),
('IA','Iowa',NULL),
('KS','Kansas',NULL),
('KY','Kentucky',NULL),
('LA','Louisiana',NULL),
('ME','Maine',NULL),
('MD','Maryland',NULL),
('MA','Massachusetts',NULL),
('MI','Michigan',NULL),
('MN','Minnesota',NULL),
('MS','Mississippi',NULL),
('MO','Missouri',NULL),
('MT','Montana',NULL),
('NE','Nebraska',NULL),
('NV','Nevada',NULL),
('NH','New Hampshire',NULL),
('NJ','New Jersey',NULL),
('NM','New Mexico',NULL),
('NY','New York',NULL),
('NC','North Carolina',NULL),
('ND','North Dakota',NULL),
('OH','Ohio',NULL),
('OK','Oklahoma',NULL),
('OR','Oregon',NULL),
('PY','Pennsylvania',NULL),
('RI','Rhode Island',NULL),
('SC','South Carolina',NULL),
('SD','South Dakota',NULL),
('TN','Tennessee',NULL),
('TX','Texas',NULL),
('UT','Utah',NULL),
('VT','Vermont',NULL),
('VA','Virginia',NULL),
('WA','Washington',NULL),
('WV','West Virginia',NULL),
('WI','Wisconsin',NULL),
('WY','Wyoming',NULL);