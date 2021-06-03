delete from "LookupLegalDocs" 
			where doc_id >= 1;
alter sequence "LookupLegalDocs_doc_id_seq"
  restart with 1;

INSERT INTO "LookupLegalDocs" ("created_at", "updated_at", "name", "target", "path") 
VALUES
(NOW(), NOW(), 'Terms of Use', 'User', 'Modo Bio TOU_FINAL dd May 2021.html'),
(NOW(), NOW(), 'Privacy Policy', 'User', 'Modo Bio Privacy Policy_FINAL dd May 2021.html');