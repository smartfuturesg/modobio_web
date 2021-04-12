delete from "LookupProfessionColors" 
			where idx >= 1;
alter sequence "LookupProfessionColors_idx_seq"
  restart with 1;

INSERT INTO "LookupProfessionColors" ("created_at", "updated_at","profession_type","icon","color") 
VALUES
('NOW()','NOW()','doctor','doctor.svg','#d71e3e'),
('NOW()','NOW()','physical_therapist','physiotherapist.svg','#fec619'),
('NOW()','NOW()','nutrition','nutritionist - 1.svg','#4661af'),
('NOW()','NOW()','trainer','physical-training.svg','#aef2ea');