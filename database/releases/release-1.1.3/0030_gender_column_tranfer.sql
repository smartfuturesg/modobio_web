DO $$

BEGIN

    UPDATE "User" SET gender =
        (SELECT gender FROM "ClientInfo"
        WHERE "User".user_id = "ClientInfo".user_id);

END;

$$ LANGUAGE plpgsql;