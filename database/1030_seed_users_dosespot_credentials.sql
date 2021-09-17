--add DoseSpot credentials to Staff ID 12 and DoseSpot Patient ID to Client 22

delete from "DoseSpotPractitionerID" 
			where idx >= 1;
alter sequence "DoseSpotPractitionerID_idx_seq"
  restart with 1;


insert into "DoseSpotPractitionerID" ("user_id", "ds_user_id", "ds_encrypted_user_id","ds_enrollment_status") values
(12, 231937, '9WwYAEtZcb8t5yne+Ep1Ex7vd9RN1wwXjShReN0yFtG6dmEZuGcrEUV5YCqNRQNQUzm6VHOqo4cvx1PxA642Cg','pending');

delete from "DoseSpotPatientID" 
			where idx >= 1;
alter sequence "DoseSpotPatientID_idx_seq"
  restart with 1;


insert into "DoseSpotPatientID" ("user_id", "ds_user_id") values
(22, 18090700);


insert into "ClientInfo" ("user_id","territory_id") values
(22,1);