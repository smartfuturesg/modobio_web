--add operational territories for seed users pro@modobio.com and name@modobio.com

delete from "DoseSpotPractitionerID" 
			where idx >= 1;
alter sequence "DoseSpotPractitionerID_idx_seq"
  restart with 1;


insert into "DoseSpotPractitionerID" ("user_id", "ds_user_id", "ds_encrypted_user_id","ds_enrollment_status") values
(12, 1, '9WwYAEtZcb8t5yne+Ep1Ex7vd9RN1wwXjShReN0yFtG6dmEZuGcrEUV5YCqNRQNQUzm6VHOqo4cvx1PxA642Cg','pending');

delete from "DoseSpotPatientID" 
			where idx >= 1;
alter sequence "DoseSpotPatientID_idx_seq"
  restart with 1;


insert into "DoseSpotPatientID" ("user_id", "ds_user_id") values
(22, 18090700);