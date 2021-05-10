
INSERT INTO "User" ("email", "firstname", "lastname", "is_staff", "is_client", "is_internal", "modobio_id", "deleted") VALUES 
('test_remote_registration@gmail.com', 'Remote', 'Client', false, true, true,'VFRGH3YSM4JX', false),
('staff_member@modobio.com', 'testy', 'testerson', true, false, true, 'KW99TSVWP883', false);

INSERT INTO "UserLogin" ("user_id", "password") VALUES 
(1, 'pbkdf2:sha256:150000$6N0cAVoO$118cbf0e7fe1806b5fca79c412ce1c334373abbf2faddb67dcc278cf8c2e5643'), 
(2, 'pbkdf2:sha256:150000$6N0cAVoO$118cbf0e7fe1806b5fca79c412ce1c334373abbf2faddb67dcc278cf8c2e5643');

