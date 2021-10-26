--add DoseSpot credentials to Staff ID 12 and DoseSpot Patient ID to Client 22

delete from "DoseSpotPractitionerID" 
			where idx >= 1;
alter sequence "DoseSpotPractitionerID_idx_seq"
  restart with 1;


insert into "DoseSpotPractitionerID" ("user_id", "ds_user_id", "ds_enrollment_status") values
(12, 227295, 'pending');

delete from "DoseSpotPatientID" 
			where idx >= 1;
alter sequence "DoseSpotPatientID_idx_seq"
  restart with 1;


insert into "DoseSpotPatientID" ("user_id", "ds_user_id") values
(22, 18090700);

