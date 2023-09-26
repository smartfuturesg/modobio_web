DO $$
DECLARE
    _staff_user_1 INTEGER;
    _staff_user_2 INTEGER;
    _staff_user_3 INTEGER;
    _staff_user_4 INTEGER;
    _staff_user_5 INTEGER;
    _staff_user_6 INTEGER;
    _staff_user_7 INTEGER;
    _staff_user_8 INTEGER;
    _staff_user_9 INTEGER;
    _pro_user_1 INTEGER;
    _pro_user_2 INTEGER;
    _pro_user_3 INTEGER;
    _pro_user_4 INTEGER;
    _pro_user_5 INTEGER;
BEGIN
    SELECT user_id INTO _staff_user_2 FROM "User"
    WHERE email = 'name@modobio.com';
    SELECT user_id INTO _staff_user_3 FROM "User"
    WHERE email = 'sys@modobio.com';
    SELECT user_id INTO _staff_user_4 FROM "User"
    WHERE email = 'staff@modobio.com';
    SELECT user_id INTO _staff_user_5 FROM "User"
    WHERE email = 'cservice@modobio.com';
    SELECT user_id INTO _staff_user_6 FROM "User"
    WHERE email = 'eleanor.heenan@modobio.com';
    SELECT user_id INTO _staff_user_7 FROM "User"
    WHERE email = 'louise.hogue@modobio.com';
    SELECT user_id INTO _staff_user_8 FROM "User"
    WHERE email = 'justin.venturi@modobio.com';
    SELECT user_id INTO _staff_user_9 FROM "User"
    WHERE email = 'dustin.king@modobio.com';
    SELECT user_id INTO _pro_user_1 FROM "User"
    WHERE email = 'doc@modobio.com';
    SELECT user_id INTO _pro_user_2 FROM "User"
    WHERE email = 'diet@modobio.com';
    SELECT user_id INTO _pro_user_3 FROM "User"
    WHERE email = 'train@modobio.com';
    SELECT user_id INTO _pro_user_4 FROM "User"
    WHERE email = 'pro@modobio.com';
    SELECT user_id INTO _pro_user_5 FROM "User"
    WHERE email = 'psych@modobio.com';
    
    INSERT INTO "TelehealthStaffSettings"
        (
         user_id, 
         auto_confirm, 
         timezone, 
         provider_telehealth_access
         )
    VALUES
        (_staff_user_2, true, 'UTC', true),
        (_staff_user_3, true, 'UTC', true),
        (_staff_user_4, true, 'UTC', true),
        (_staff_user_6, true, 'UTC', true),
        (_staff_user_7, true, 'UTC', true),
        (_staff_user_8, true, 'UTC', true), 
        (_staff_user_9, true, 'UTC', true),
        (_pro_user_1, true, 'UTC', true),
        (_pro_user_2, true, 'UTC', true),
        (_pro_user_3, true, 'UTC', true),
        (_pro_user_4, true, 'UTC', true),
        (_pro_user_5, true, 'UTC', true);

END;

$$ LANGUAGE plpgsql;
