DO $$
DECLARE 
    _user_id INTEGER;
    _team_member_a INTEGER;
    _team_member_b INTEGER;
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
        dob)
    VALUES (
        'client@modobio.com',
        'TC12JASDFF12',
        'Bernie',
        'Focker',
        false,
		false,
        true,
        true,
        false,
        '1990-06-01')
    RETURNING user_id INTO _user_id;

    INSERT INTO "UserLogin" (
        user_id,
        password)
    VALUES (
        _user_id,
        'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1');

    INSERT INTO "ClientInfo" (user_id, membersince, zipcode, territory_id)
    VALUES (_user_id, '2021-01-01', '85255', 1);

    INSERT INTO "UserSubscriptions" (
        user_id,
        is_staff,
        start_date,
        subscription_status
        )
    VALUES (
        _user_id,
        false,
        '2021-01-01',
        'unsubscribed');

    -- Create a care team with two staff members.

    -- SELECT and INTO cannot be split across lines?
    SELECT user_id INTO _team_member_a FROM "User"
    WHERE email = 'name@modobio.com';

    SELECT user_id INTO _team_member_b FROM "User"
    WHERE email = 'pro@modobio.com';

    INSERT INTO "ClientClinicalCareTeam" (user_id, team_member_user_id, is_temporary)
    VALUES
        (_user_id, _team_member_a, false),
        (_user_id, _team_member_b, false);

    INSERT INTO "ClientClinicalCareTeamAuthorizations" (
        user_id,
        team_member_user_id,
        resource_id,
        status)
    SELECT _user_id, _team_member_a, resources.resource_id, 'accepted'
    FROM "LookupClinicalCareTeamResources" AS resources;

    INSERT INTO "ClientClinicalCareTeamAuthorizations" (
        user_id,
        team_member_user_id,
        resource_id,
        status)
    SELECT _user_id, _team_member_b, resources.resource_id, 'accepted'
    FROM "LookupClinicalCareTeamResources" AS resources;

    -- Add DoseSpot credentials.
    INSERT INTO "DoseSpotPatientID" (user_id, ds_user_id)
    VALUES (_user_id, 18090700);
END;
$$ LANGUAGE plpgsql;
