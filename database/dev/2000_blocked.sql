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
        'blocked.test@modobio.com',
        'TC13JASDFF82',
        'Blocked',
        'Account',
        false,
		false,
        true,
        true,
        true,
        'm',
        '1990-01-01')
    RETURNING user_id INTO _user_id;

    INSERT INTO "UserLogin"
        (
         user_id,
         client_account_blocked,
         client_account_blocked_reason,
         password
         )
    VALUES
        (
         _user_id,
         true,
         'Blocked for testing purposes',
         'pbkdf2:sha256:150000$DdCwxwL8$c4f7e8c7179c47b8ec96b57e702bbcc83a98ea13575dfd74ca11b88f4069b3f1'
         );

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

END;

$$ LANGUAGE plpgsql;