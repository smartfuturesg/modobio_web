DO $$
DECLARE
    _user_id INTEGER;
BEGIN

    INSERT INTO "User"
        (
         modobio_id,
         email,
         firstname,
         lastname,
         is_staff,
         is_client,
         biological_sex_male,
         email_verified,
         dob,
         was_staff,
         gender
         )
    VALUES
        (
         'XFB1SN3GM512',
         'name@modobio.com',
         'First',
         'Last',
         true,
         false,
         false,
         true,
         '1970-01-01',
         true,
         'm'
         ) RETURNING user_id INTO _user_id;

    INSERT INTO "UserLogin"
        (
         user_id,
         password
         )
    VALUES
        (
         _user_id,
         'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'
         );

    INSERT INTO "StaffProfile"
        (
         user_id,
         membersince
         )
    VALUES
        (
         _user_id,
         '2021-01-01'
         );

    INSERT INTO "StaffRoles"
        (
         user_id,
         role
         )
    VALUES
        (_user_id, 'system_admin'),
        (_user_id, 'staff_admin'),
        (_user_id, 'client_services'),
        (_user_id, 'community_manager');

END;

$$ LANGUAGE plpgsql;