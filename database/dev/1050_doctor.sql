DO $$
DECLARE
    _user_id INTEGER;
    _role_id INTEGER;
    _country_id INTEGER;
BEGIN
    INSERT INTO "User" (
        email,
        modobio_id,
        firstname,
        lastname,
        is_staff,
		was_staff,
        is_client,
        is_provider,
        email_verified,
        biological_sex_male,
        gender,
        dob)
    VALUES (
        'doc@modobio.com',
        'KW99TSVWP812',
        'Jonathan',
        'Crane',
        false,
		true,
        false,
        true,
        true,
        true,
        'm',
        '1976-03-19')
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
    VALUES (_user_id, 'medical_doctor');

    SELECT idx INTO _role_id FROM "StaffRoles"
    WHERE role = 'medical_doctor' AND user_id = _user_id;

    SELECT idx INTO _country_id FROM "LookupCountriesOfOperations"
    WHERE LOWER(country) = 'usa';

    INSERT INTO "StaffOperationalTerritories" (
        user_id,
        operational_territory_id,
        role_id)
    SELECT _user_id, idx, _role_id
    FROM "LookupTerritoriesOfOperations";

    INSERT INTO "PractitionerCredentials" (
        user_id,
        country_id,
        state,
        credential_type,
        credentials,
        status,
        role_id
        )
    VALUES
        (_user_id, _country_id, NULL, 'npi', '1296336567', 'Verified', _role_id),
        (_user_id, _country_id, 'CA', 'dea', '43218470', 'Verified', _role_id),
        (_user_id, _country_id, 'FL', 'med_lic', '21323512', 'Verified', _role_id);
END;
$$ LANGUAGE plpgsql;
