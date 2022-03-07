import os

from werkzeug.security import generate_password_hash

passw = os.getenv('MODOBIO_WEARABLES_PASS')
if not passw:
    raise ValueError('MODOBIO_WEARABLES_PASS not set.')

passw_hash = generate_password_hash(passw)

sql = f"""
DO $$
DECLARE wearables_user_id INTEGER;
BEGIN
    INSERT INTO "LookupRoles" (
        role_name,
        display_name,
        is_practitioner,
        has_client_data_access)
    VALUES (
        'wearables_scraper',
        'Wearbles data scraper',
        false,
        true);

    INSERT INTO "User" (
        email,
        modobio_id,
        firstname,
        lastname,
        is_staff,
        was_staff,
        is_client,
        email_verified)
    VALUES (
        'wearables_scraper@modobio.com',
        'WRBLSCRPR000',
        'Wearables',
        'Scraper',
        true,
        true,
        false,
        true)
    RETURNING user_id INTO wearables_user_id;

    INSERT INTO "UserLogin" (
        user_id,
        password)
    VALUES (
        wearables_user_id,
        '{passw_hash}');

    INSERT INTO "StaffRoles" (
        user_id,
        role)
    VALUES (
        wearables_user_id,
        'wearables_scraper');
END $$;
"""
