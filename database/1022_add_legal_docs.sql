delete from "LookupLegalDocs" 
			where doc_id >= 1;
alter sequence "LookupLegalDocs_doc_id_seq"
  restart with 1;

INSERT INTO "LookupMacroGoals" ("name", "target", "path") 
VALUES
("Terms of Use", "User", "Modo Bio TOU_FINAL dd May 2021.DOCX"),
("Privacy Policy", "User", "Modo Bio Privacy Policy_FINAL dd May 2021.DOCX");