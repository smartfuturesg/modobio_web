-- Updated User to fill in was_staff based on the value of is_staff

UPDATE "User" 
	SET was_staff = is_staff
WHERE was_staff IS NULL