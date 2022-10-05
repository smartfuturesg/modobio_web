DO $$
DECLARE
    _user_id INTEGER;
BEGIN
    INSERT INTO "User" (
        email,
        modobio_id,
        firstname,
        lastname,
        is_staff,
		was_staff,
        is_client,
        email_verified,
        biological_sex_male,
        gender,
        dob)
    VALUES (
        'sys@modobio.com',
        'VFRGH3YSM412',
        'Neo',
        'Anderson',
        true,
		true,
        false,
        true,
        true,
        'm',
        '1975-01-01')
    RETURNING user_id INTO _user_id;

    INSERT INTO "UserLogin" (
        user_id,
        password)
    VALUES (
        _user_id,
        'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1');

    INSERT INTO "StaffProfile" (user_id, membersince)
    VALUES (_user_id, '2021-01-01');

    INSERT INTO "StaffRoles" (user_id, role)
    VALUES (_user_id, 'system_admin');

END;
$$ LANGUAGE plpgsql;
