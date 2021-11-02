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
        is_client,
        email_verified,
        biological_sex_male,
        dob)
    VALUES (
        'matej.kubinec@sde.cz',
        'JAF04LYTZN12',
        'Matej',
        'Kubinec',
        true,
        false,
        true,
        true,
        '1990-06-01')
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
    VALUES
        (_user_id, 'system_admin'),
        (_user_id, 'staff_admin'),
        (_user_id, 'client_services'),
        (_user_id, 'medical_doctor'),
        (_user_id, 'physical_therapist'),
        (_user_id, 'nutritionist'),
        (_user_id, 'trainer');
END;
$$ LANGUAGE plpgsql;
