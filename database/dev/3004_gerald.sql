DO $$
DECLARE
    _user_id INTEGER;
    _team_member_a INTEGER;
    _team_member_b INTEGER;
    _team_member_c INTEGER;
    _team_member_d INTEGER;
    _team_member_e INTEGER;

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
        'gerald.martinez@modobio.com',
        'XY97KBSENZ19',
        'Gerald',
        'Martinez',
        false,
		false,
        true,
        true,
        true,
        'm',
        '1995-10-08')
    RETURNING user_id INTO _user_id;

    INSERT INTO "UserLogin" (
        user_id,
        password)
    VALUES (
        _user_id,
        'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1');

    INSERT INTO "ClientInfo" (user_id, membersince, zipcode, territory_id)
    VALUES (_user_id, '2021-01-01', '85255', 1);

    INSERT INTO "UserSubscriptions"
        (
         user_id,
         is_staff,
         start_date,
         subscription_status,
         subscription_type_id,
         last_checked_date,
         expire_date
        )
    VALUES
        (
         _user_id,
         false,
         CURRENT_DATE,
         'subscribed',
         3,
         CURRENT_DATE,
         CURRENT_DATE + interval '1 year'
        );

    SELECT user_id INTO _team_member_a FROM "User"
    WHERE email = 'vilma.esparza@modobio.com';
    SELECT user_id INTO _team_member_b FROM "User"
    WHERE email = 'louise.hogue@modobio.com';
    SELECT user_id INTO _team_member_c FROM "User"
    WHERE email = 'justin.venturi@modobio.com';
    SELECT user_id INTO _team_member_d FROM "User"
    WHERE email = 'dustin.king@modobio.com';
    SELECT user_id INTO _team_member_e FROM "User"
    WHERE email = 'eleanor.heenan@modobio.com';

    INSERT INTO "ClientClinicalCareTeam"
        (
         user_id,
         team_member_user_id,
         is_temporary
         )
    VALUES
        (_user_id, _team_member_a, false),
        (_user_id, _team_member_b, false),
        (_user_id, _team_member_c, false),
        (_user_id, _team_member_d, false),
        (_user_id, _team_member_e, false);

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

    INSERT INTO "ClientClinicalCareTeamAuthorizations" (
        user_id,
        team_member_user_id,
        resource_id,
        status)
    SELECT _user_id, _team_member_c, resources.resource_id, 'accepted'
    FROM "LookupClinicalCareTeamResources" AS resources;

    INSERT INTO "ClientClinicalCareTeamAuthorizations" (
        user_id,
        team_member_user_id,
        resource_id,
        status)
    SELECT _user_id, _team_member_d, resources.resource_id, 'accepted'
    FROM "LookupClinicalCareTeamResources" AS resources;

    INSERT INTO "ClientClinicalCareTeamAuthorizations" (
        user_id,
        team_member_user_id,
        resource_id,
        status)
    SELECT _user_id, _team_member_e, resources.resource_id, 'accepted'
    FROM "LookupClinicalCareTeamResources" AS resources;

END;

$$ LANGUAGE plpgsql;