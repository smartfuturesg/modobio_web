delete from "LookupMedicalSymptoms" 
			where idx >= 1;
alter sequence "LookupMedicalSymptoms_idx_seq"
  restart with 1;

INSERT INTO "LookupMedicalSymptoms" ("created_at", "updated_at", "name", "code") 
VALUES
(NOW(), NOW(), 'Abdominal Pain', 'R10.84'),
(NOW(), NOW(), 'Anaphylaxis', 'T78.2'),
(NOW(), NOW(), 'Anxiety', 'F41.9'),
(NOW(), NOW(), 'Blurred Vision', 'H53.8'),
(NOW(), NOW(), 'Chest Tightness', 'R07.9'),
(NOW(), NOW(), 'Diarrhea', 'R19.7'),
(NOW(), NOW(), 'Dizziness', 'R42'),
(NOW(), NOW(), 'Facial Swelling', 'R22.0'),
(NOW(), NOW(), 'Fainting', 'R55'),
(NOW(), NOW(), 'Headache/Migraine', 'R51'),
(NOW(), NOW(), 'Hives', 'L50.9'),
(NOW(), NOW(), 'Itching', 'L29.9'),
(NOW(), NOW(), 'Joint Pain', 'M25.50'),
(NOW(), NOW(), 'Kidney Injury', 'N14.1'),
(NOW(), NOW(), 'Leg Edema/Swelling', 'R22.43'),
(NOW(), NOW(), 'Lip Swelling', 'R22.0'),
(NOW(), NOW(), 'Liver Damage', 'K71.9'),
(NOW(), NOW(), 'Nausea', 'R11.0'),
(NOW(), NOW(), 'Palpitations', 'R00.2'),
(NOW(), NOW(), 'Photo (light) Sensitivity', 'L56.8'),
(NOW(), NOW(), 'Rash', 'R21'),
(NOW(), NOW(), 'Shortness of Breath', 'R06.02'),
(NOW(), NOW(), 'Skin Irritation', 'L98.9'),
(NOW(), NOW(), 'Throat Swelling', 'R22.1'),
(NOW(), NOW(), 'Vertigo', 'R42'),
(NOW(), NOW(), 'Vomiting', 'R11.10'),
(NOW(), NOW(), 'Wheezing', 'R06.2');