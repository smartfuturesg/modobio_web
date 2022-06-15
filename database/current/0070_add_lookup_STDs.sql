-----------------------------
-- Empty table and reset index. 
-- Rather than altering the table, this script inserts data 
-- So to avoid duplicates, we empty the table and reindex.
-- This is a solution that should be run only once on 
-- persistent databases. 
-- Further changes to this table will be done through the API
-----------------------------


delete from "LookupSTDs" 
	where std_id >= 1;

alter sequence "LookupSTDs_std_id_seq"
			restart with 1;

INSERT INTO "LookupSTDs" ("std_id","std") 
VALUES 
(1,'Chancroid'),
(2,'Chlamydia'),
(3,'Crabs (Pubic Lice)'),
(4,'Gonorrhea'),
(5,'Hepatitis'),
(6,'Herpes'),
(7,'HIV/AIDS'),
(8,'Human Papillomavirus and Genital Warts'),
(9,'Lymphogranuloma Venereum'),
(10,'Molluscum Contagiosum'),
(11,'Nongonococcal Urethritis'),
(12,'Pelvic Inflammatory Disease'),
(13,'Scabies'),
(14,'Syphilis'),
(15,'Trichomoniasis'),
(16,'Vaginal Yeast Infection'),
(17,'Bacterial Vaginosis'),
(18,'Yeast Infection in Men'),
(19,'Balanitis'),
(20,'Cytomegalovirus'),
(21,'Mycoplasma'),
(22,'Mononucleosis');