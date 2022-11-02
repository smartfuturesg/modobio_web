DO $$

DECLARE
    _user_id_a INTEGER;
    _user_id_b INTEGER;
    _user_id_c INTEGER;
    _team_member_id_a INTEGER;
    _team_member_id_b INTEGER;
    _team_member_id_c INTEGER;


BEGIN

    -- Bernie has Vilma
    SELECT user_id INTO _user_id_a FROM "User"
    WHERE email = 'client@modobio.com';
    SELECT user_id INTO _team_member_id_a FROM "User"
    WHERE email = 'vilma.esparza@modobio.com';

    -- Cynthia has James
    SELECT user_id INTO _user_id_b FROM "User"
    WHERE email = 'cynthia.mears@modobio.com';
    SELECT user_id INTO _team_member_id_b FROM "User"
    WHERE email = 'james.mears@modobio.com';
    -- Vilma has Pam K
    SELECT user_id INTO _user_id_c FROM "User"
    WHERE email = 'vilma.esparza@modobio.com';
    SELECT user_id INTO _team_member_id_c FROM "User"
    WHERE email = 'pam.koehler@modobio.com';

    INSERT INTO "ClientClinicalCareTeam"
        (
         user_id,
         team_member_user_id,
         is_temporary
         )
    VALUES
        (_user_id_a, _team_member_id_a, false),
        (_user_id_b, _team_member_id_b, false),
        (_user_id_c, _team_member_id_c, false);

    INSERT INTO "ClientClinicalCareTeamAuthorizations" (
        user_id,
        team_member_user_id,
        resource_id,
        status)
    SELECT _user_id_a, _team_member_id_a, resources.resource_id, 'accepted'
    FROM "LookupClinicalCareTeamResources" AS resources;
    INSERT INTO "ClientClinicalCareTeamAuthorizations" (
        user_id,
        team_member_user_id,
        resource_id,
        status)
    SELECT _user_id_b, _team_member_id_b, resources.resource_id, 'accepted'
    FROM "LookupClinicalCareTeamResources" AS resources;
    INSERT INTO "ClientClinicalCareTeamAuthorizations" (
        user_id,
        team_member_user_id,
        resource_id,
        status)
    SELECT _user_id_c, _team_member_id_c, resources.resource_id, 'accepted'
    FROM "LookupClinicalCareTeamResources" AS resources;

END;

$$ LANGUAGE plpgsql;