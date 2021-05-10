INSERT INTO "User" ("email", "firstname", "lastname", "is_staff", "is_client", "is_internal", "modobio_id", "deleted", "biological_sex_male") VALUES 
('sys@modobio.com', 'Sys', 'User', true, false, true,'VFRGH3YSM4JQ', false, true),
('doc@modobio.com', 'Doc', 'User', true, false, true, 'KW99TSVWP884', false, true),
('docext@modobio.com', 'DocExt', 'User', true, false, false, 'PUR27NVP3083', false, true),
('physio@modobio.com', 'Physio', 'User', true, false, true, 'FG86DG4Q3J72', false, true),
('physioext@modobio.com', 'PhysioExt', 'User', true, false, false, 'TQ9N2M9SMQL8', false, true),
('nutri@modobio.com', 'Nutri', 'User', true, false, true, 'RW0QZK442FRR', false, true),
('nutriext@modobio.com', 'NutriExt', 'User', true, false, false, 'FPQLX97G6KGN', false, true),
('train@modobio.com', 'Train', 'User', true, false, true, 'QE6RS18753CH', false, true),
('trainext@modobio.com', 'TrainExt', 'User', true, false, false, 'FL6SB69RQWR7', false, true),
('pro@modobio.com', 'Pro', 'User', true, false, true, 'EXK7322KFN2G', false, true),
('proext@modobio.com', 'ProExt', 'User', true, false, false, 'FXF0450R7X6L', false, true),
('staff@modobio.com', 'Staff', 'User', true, false, true, 'BHBCBZBW4K48', false, true),
('cservice@modobio.com', 'ClientServices', 'User', true, false, true, 'BX4NW9897R40', false, true),
('name@modobio.com', 'FirstName', 'LastName', true, false, true, 'XFB1SN3GM59J', false, true),
('david.kubos@sde.cz', 'David', 'Kubos', true, false, true, 'EJP05FH6054T', false, true),
('tomas.blazek@sde.cz', 'Tomas', 'Blazek', true, false, true, 'MT5M08SCL6CQ', false, true),
('aneta.opletalova@sde.cz', 'Aneta', 'Opletalova', true, false, true, 'OF0K861W7J8Q', false, true),
('jakub.freywald@sde.cz', 'Jakub', 'Freywald', true, false, true, 'UJPH98Q8KPG6', false, true),
('matej.kubinec@sde.cz', 'Matej', 'Kubinec', true, false, true, 'JAF04LYTZN9W', false, true),
('sebastian.brostl@sde.cz', 'Sebastian', 'Brostl', true, false, true, 'VLCZG2Z2ZL5H', false, true),
('lukas.krajci@sde.cz', 'Lukas', 'Krajci', true, false, true, 'VS071YRSQ98Z', false, true),
('client@modobio.com', 'Test', 'Client', false, true, false, 'TC12JASDFF18', false, true);

INSERT INTO "UserLogin" ("user_id", "password") VALUES 
(1, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(2, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(3, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(4, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(5, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(6, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(7, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(8, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(9, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(10, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(11, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(12, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(13, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(14, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(15, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(16, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(17, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(18, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(19, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(20, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(21, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'),
(22, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1');

INSERT INTO "ClientInfo" ("user_id") VALUES
(22);

INSERT INTO "StaffRoles" ("user_id", "role", "verified") VALUES 
(1, 'system_admin', false), 
(2, 'doctor', false), 
(3, 'doctor', false), 
(4, 'physical_therapist', false), 
(5, 'physical_therapist', false), 
(6, 'nutrition', false),  
(7, 'nutrition', false),  
(8, 'trainer', false), 
(9, 'trainer', false), 
(10, 'doctor', false), 
(10, 'physical_therapist', false), 
(10, 'nutrition', false), 
(10, 'trainer', false), 
(11, 'doctor', false), 
(11, 'physical_therapist', false), 
(11, 'nutrition', false), 
(11, 'trainer', false), 
(12, 'staff_admin', false), 
(13, 'client_services', false), 
(14, 'system_admin', false), 
(14, 'staff_admin', false), 
(14, 'client_services', false), 
(14, 'doctor', false), 
(14, 'physical_therapist', false), 
(14, 'nutrition', false), 
(14, 'trainer', false), 
(15, 'system_admin', false), 
(15, 'staff_admin', false), 
(15, 'client_services', false), 
(15, 'doctor', false), 
(15, 'physical_therapist', false), 
(15, 'nutrition', false), 
(15, 'trainer', false), 
(16, 'system_admin', false), 
(16, 'staff_admin', false), 
(16, 'client_services', false), 
(16, 'doctor', false), 
(16, 'physical_therapist', false), 
(16, 'nutrition', false), 
(16, 'trainer', false), 
(17, 'system_admin', false), 
(17, 'staff_admin', false), 
(17, 'client_services', false), 
(17, 'doctor', false), 
(17, 'physical_therapist', false), 
(17, 'nutrition', false), 
(17, 'trainer', false), 
(18, 'system_admin', false), 
(18, 'staff_admin', false), 
(18, 'client_services', false), 
(18, 'doctor', false), 
(18, 'physical_therapist', false), 
(18, 'nutrition', false), 
(18, 'trainer', false), 
(19, 'system_admin', false), 
(19, 'staff_admin', false), 
(19, 'client_services', false), 
(19, 'doctor', false), 
(19, 'physical_therapist', false), 
(19, 'nutrition', false), 
(19, 'trainer', false), 
(20, 'system_admin', false), 
(20, 'staff_admin', false), 
(20, 'client_services', false), 
(20, 'doctor', false), 
(20, 'physical_therapist', false), 
(20, 'nutrition', false), 
(20, 'trainer', false), 
(21, 'system_admin', false), 
(21, 'staff_admin', false), 
(21, 'client_services', false), 
(21, 'doctor', false), 
(21, 'physical_therapist', false), 
(21, 'nutrition', false), 
(21, 'trainer', false);