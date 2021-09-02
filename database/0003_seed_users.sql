INSERT INTO "User" ("user_id", "email", "firstname", "lastname", "is_staff", "is_client", "is_internal", "modobio_id", "deleted", "email_verified", "biological_sex_male") VALUES 
(1, 'sys@modobio.com', 'Sys', 'User', true, false, true,'VFRGH3YSM412', false, true, true),
(2, 'doc@modobio.com', 'Doc', 'User', true, false, true, 'KW99TSVWP812', false, true, true),
(3, 'docext@modobio.com', 'DocExt', 'User', true, false, false, 'PUR27NVP3012', false, true, false),
(4, 'physio@modobio.com', 'Physio', 'User', true, false, true, 'FG86DG4Q3J12', false, true, false),
(5, 'physioext@modobio.com', 'PhysioExt', 'User', true, false, false, 'TQ9N2M9SMQ12', false, true, true),
(6, 'nutri@modobio.com', 'Nutri', 'User', true, false, true, 'RW0QZK442F12', false, true, false),
(7, 'nutriext@modobio.com', 'NutriExt', 'User', true, false, false, 'FPQLX97G6K12', false, true, true),
(8, 'train@modobio.com', 'Train', 'User', true, false, true, 'QE6RS1875312', false, true, false),
(9, 'trainext@modobio.com', 'TrainExt', 'User', true, false, false, 'FL6SB69RQW12', false, true, true),
(10, 'pro@modobio.com', 'Pro', 'User', true, false, true, 'EXK7322KFN12', false, true, true),
(11, 'proext@modobio.com', 'ProExt', 'User', true, false, false, 'FXF0450R7X12', false, true, false),
(12, 'staff@modobio.com', 'Staff', 'User', true, false, true, 'BHBCBZBW4K12', false, true, false),
(13, 'cservice@modobio.com', 'ClientServices', 'User', true, false, true, 'BX4NW9897R12', false, true, true),
(14, 'name@modobio.com', 'FirstName', 'LastName', true, false, true, 'XFB1SN3GM512', false, true, true),
(15, 'david.kubos@sde.cz', 'David', 'Kubos', true, false, true, 'EJP05FH60512', false, true, true),
(16, 'tomas.blazek@sde.cz', 'Tomas', 'Blazek', true, false, true, 'MT5M08SCL612', false, true, true),
(17, 'aneta.opletalova@sde.cz', 'Aneta', 'Opletalova', true, false, true, 'OF0K861W7J12', false, true, false),
(18, 'jakub.freywald@sde.cz', 'Jakub', 'Freywald', true, false, true, 'UJPH98Q8KP12', false, true, true),
(19, 'matej.kubinec@sde.cz', 'Matej', 'Kubinec', true, false, true, 'JAF04LYTZN12', false, true, true),
(20, 'sebastian.brostl@sde.cz', 'Sebastian', 'Brostl', true, false, true, 'VLCZG2Z2ZL12', false, true, true),
(21, 'lukas.krajci@sde.cz', 'Lukas', 'Krajci', true, false, true, 'VS071YRSQ912', false, true, true),
(22, 'client@modobio.com', 'Test', 'Client', false, true, false, 'TC12JASDFF12', false, true, false),
(30, 'alejandro.lorenzo+wheel_clinician_md1@atlanticventurepartners.tech', 'Modo Bio', 'MD1', true, false, false, 'MD52MAVDIF41', false, true, false),
(31, 'alejandro.lorenzo+wheel_clinician_md2@atlanticventurepartners.tech', 'Modo Bio', 'MD2', true, false, false, 'MD43LBUEHG32', false, true, true),
(32, 'alejandro.lorenzo+wheel_clinician_np1@atlanticventurepartners.tech', 'Modo Bio', 'NP1', true, false, false, 'NP34KCTFGH23', false, true, false),
(33, 'alejandro.lorenzo+wheel_clinician_np2@atlanticventurepartners.tech', 'Modo Bio', 'NP2', true, false, false, 'NP25JDSGFI14', false, true, true);

ALTER SEQUENCE "User_user_id_seq"
		RESTART WITH 34;


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
(22, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'),
(30, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(31, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'), 
(32, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'),
(33, 'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1');

INSERT INTO "ClientInfo" ("user_id", "membersince") VALUES
(22, '2021-01-01');

INSERT INTO "UserSubscriptions" ("user_id", "is_staff", "start_date", "subscription_status", "subscription_type_id") VALUES
(22, false, '2021-01-01', 'unsubscribed', 1);

INSERT INTO "StaffProfile" ("user_id", "membersince") VALUES
(1, '2021-01-01'),
(2, '2021-01-01'),
(3, '2021-01-01'),
(4, '2021-01-01'),
(5, '2021-01-01'),
(6, '2021-01-01'),
(7, '2021-01-01'),
(8, '2021-01-01'),
(9, '2021-01-01'),
(10, '2021-01-01'),
(11, '2021-01-01'),
(12, '2021-01-01'),
(13, '2021-01-01'),
(14, '2021-01-01'),
(15, '2021-01-01'),
(16, '2021-01-01'),
(17, '2021-01-01'),
(18, '2021-01-01'),
(19, '2021-01-01'),
(20, '2021-01-01'),
(21, '2021-01-01'),
(30, '2021-01-01'),
(31, '2021-01-01'),
(32, '2021-01-01'),
(33, '2021-01-01');

INSERT INTO "StaffRoles" ("user_id", "role", "granter_id") VALUES 
(1, 'system_admin', 14), 
(2, 'medical_doctor', 14), 
(3, 'medical_doctor', 14), 
(4, 'physical_therapist', 14), 
(5, 'physical_therapist', 14), 
(6, 'nutritionist', 14),  
(7, 'nutritionist', 14),  
(8, 'trainer', 14), 
(9, 'trainer', 14), 
(10, 'medical_doctor', 14), 
(10, 'physical_therapist', 14), 
(10, 'nutritionist', 14), 
(10, 'trainer', 14), 
(11, 'medical_doctor', 14), 
(11, 'physical_therapist', 14), 
(11, 'nutritionist', 14), 
(11, 'trainer', 14), 
(12, 'staff_admin', 14), 
(13, 'client_services', 14), 
(14, 'system_admin', 14), 
(14, 'staff_admin', 14), 
(14, 'client_services', 14), 
(14, 'medical_doctor', 14), 
(14, 'physical_therapist', 14), 
(14, 'nutritionist', 14), 
(14, 'trainer', 14), 
(15, 'system_admin', 14), 
(15, 'staff_admin', 14), 
(15, 'client_services', 14), 
(15, 'medical_doctor', 14), 
(15, 'physical_therapist', 14), 
(15, 'nutritionist', 14), 
(15, 'trainer', 14), 
(16, 'system_admin', 14), 
(16, 'staff_admin', 14), 
(16, 'client_services', 14), 
(16, 'medical_doctor', 14), 
(16, 'physical_therapist', 14), 
(16, 'nutritionist', 14), 
(16, 'trainer', 14), 
(17, 'system_admin', 14), 
(17, 'staff_admin', 14), 
(17, 'client_services', 14), 
(17, 'medical_doctor', 14), 
(17, 'physical_therapist', 14), 
(17, 'nutritionist', 14), 
(17, 'trainer', 14), 
(18, 'system_admin', 14), 
(18, 'staff_admin', 14), 
(18, 'client_services', 14), 
(18, 'medical_doctor', 14), 
(18, 'physical_therapist', 14), 
(18, 'nutritionist', 14), 
(18, 'trainer', 14), 
(19, 'system_admin', 14), 
(19, 'staff_admin', 14), 
(19, 'client_services', 14), 
(19, 'medical_doctor', 14), 
(19, 'physical_therapist', 14), 
(19, 'nutritionist', 14), 
(19, 'trainer', 14), 
(20, 'system_admin', 14), 
(20, 'staff_admin', 14), 
(20, 'client_services', 14), 
(20, 'medical_doctor', 14), 
(20, 'physical_therapist', 14), 
(20, 'nutritionist', 14), 
(20, 'trainer', 14), 
(21, 'system_admin', 14), 
(21, 'staff_admin', 14), 
(21, 'client_services', 14), 
(21, 'medical_doctor', 14), 
(21, 'physical_therapist', 14), 
(21, 'nutritionist', 14), 
(30, 'medical_doctor', 14),
(31, 'medical_doctor', 14), 
(32, 'nurse_practitioner', 14), 
(33, 'nurse_practitioner', 14); 


insert into "TelehealthStaffSettings" ("user_id", "auto_confirm", "timezone") Values
(30, true, 'UTC'),
(31, true, 'UTC'),
(32, true, 'UTC'),
(33, true, 'UTC');