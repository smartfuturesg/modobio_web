delete from "LookupLegalDocs" 
			where idx >= 1;
alter sequence "LookupLegalDocs_idx_seq"
  restart with 1;

INSERT INTO "LookupLegalDocs" ("created_at", "updated_at", "name", "version", "target", "path") 
VALUES
(NOW(), NOW(), 'Terms of Use', 1, 'User', 'Modo Bio TOU_FINAL dd May 2021.html'),
(NOW(), NOW(), 'Privacy Policy', 1, 'User', 'Modo Bio Privacy Policy_FINAL dd May 2021.html');