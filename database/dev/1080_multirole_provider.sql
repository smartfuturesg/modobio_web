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
        dob
        )
    VALUES (
        'pro@modobio.com',
        'EXK7322KFN12',
        'Jackie',
        'Moon',
        false,
		true,
        false,
        true,
        true,
        true,
        'm',
        '1941-09-12'
        )
    RETURNING user_id INTO _user_id;

    INSERT INTO "UserLogin" (
        user_id,
        password)
    VALUES (
        _user_id,
        'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1');

    INSERT INTO "StaffProfile" (user_id, membersince)
    VALUES (_user_id, '2021-01-01');

    INSERT INTO "StaffRoles" (user_id, role, consult_rate)
    VALUES
        (_user_id, 'medical_doctor', '150.00'),
        (_user_id, 'therapist', '95.00'),
        (_user_id, 'dietitian', '100.00'),
        (_user_id, 'trainer', '125.00');

    -- NOTE: StaffOperationalTerritories is obsolete, but will be kept
    -- until we can safely remove it. PractitionerCredentials will take
    -- its place, so it is also filled out here
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
        role_id,
        want_to_practice)
    VALUES
        (_user_id, _country_id, Null, 'npi', '1296336567', 'Verified', _role_id, true),
        (_user_id, _country_id, 'FL', 'dea', '183451435', 'Verified', _role_id, true),
        (_user_id, _country_id, 'CA', 'dea', '123342534', 'Verified', _role_id, true),
        (_user_id, _country_id, 'FL', 'med_lic', '523746512', 'Verified', _role_id, true),
        (_user_id, _country_id, 'CA', 'med_lic', '839547692', 'Verified', _role_id, true);

END;
$$ LANGUAGE plpgsql;
