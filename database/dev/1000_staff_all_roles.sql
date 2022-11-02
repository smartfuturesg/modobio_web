DO $$
DECLARE
    _user_id INTEGER;
    _role_id INTEGER;
    _country_id INTEGER;

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
         true,
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
        (_user_id, 'medical_doctor'),
        (_user_id, 'therapist'),
        (_user_id, 'trainer'),
        (_user_id, 'dietitian'),
        (_user_id, 'community_manager');

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
        (_user_id, _country_id, NULL, 'npi', '1296336567', 'Verified', _role_id, true),
        (_user_id, _country_id, 'CA', 'dea', '43218470', 'Verified', _role_id, true),
        (_user_id, _country_id, 'FL', 'med_lic', '21323512', 'Verified', _role_id, true);

    -- Add DoseSpot credentials.
    INSERT INTO "DoseSpotPractitionerID" (user_id, ds_user_id, ds_enrollment_status)
    VALUES (_user_id, 227295, 'pending');

END;

$$ LANGUAGE plpgsql;