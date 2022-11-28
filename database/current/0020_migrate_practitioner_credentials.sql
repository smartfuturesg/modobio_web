-- migrate ProviderCredentials to ProviderCredentials

INSERT INTO "ProviderCredentials" ("created_at", "updated_at", "country_id", "state", "credential_type", "credentials", "status", "role_id", "expiration_date", "user_id")
SELECT "created_at", "updated_at", "country_id", "state", "credential_type", "credentials", "status", "role_id", "expiration_date", "user_id" from "ProviderCredentials";