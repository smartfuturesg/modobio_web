UPDATE public."LookupLegalDocs"
SET "path"='Modo Bio Privacy Policy August 2022.html', "version"="version" + 1
WHERE "name" = 'Privacy Policy';

UPDATE public."LookupLegalDocs"
SET "path"='Modo Bio TOU October 2022.html', "version"="version" + 1
WHERE "name" = 'Terms of Use';

INSERT INTO public."LookupLegalDocs"
("name", "target", "path", "version")
VALUES('Provider BAA', 'Provider', 'BAA Covered Entity 9 22 2222.html', 1);