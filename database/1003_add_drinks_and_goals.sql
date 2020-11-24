DO $$
DECLARE
  x integer;
  query varchar := 'select count(*) from "LookupDrinkIngredients"';
  query2 varchar := 'select count(*) from "LookupDrinks"';
  query3 varchar := 'select count(*) from "LookupGoals"';
BEGIN 
execute query into x;
  IF x >= 1 THEN
   execute 
   		'delete from "LookupDrinkIngredients" 
			where idx >= 1;
		alter sequence "LookupDrinkIngredients_idx_seq"
			restart with 1;';
  END IF;
execute query2 into x;
  IF x >= 1 THEN
   execute 
   		'delete from "LookupDrinks" 
			where drink_id >= 1;
		alter sequence "LookupDrinks_drink_id_seq"
			restart with 1;';
  END IF;
execute query3 into x;
  IF x >= 1 THEN
   execute 
   		'delete from "LookupGoals" 
			where goal_id >= 1;
		alter sequence "LookupGoals_goal_id_seq"
			restart with 1;';
  END IF;  
END $$;

INSERT INTO "LookupGoals" ("goal_name", "goal_id") 
VALUES
('Recovery', 1),
('Weight Loss', 2),
('Sharp Mind', 3),
('Gut Health', 4),
('Better Sleep', 5),
('Immune Boost', 6),
('Stamina Boost', 7),
('Anti-Aging', 8);

INSERT INTO "LookupDrinks" ("drink_id", "primary_goal_id", "color")
VALUES
(1, 1, 'Burgundy'),
(2, 2, 'Dark Green'),
(3, 3, 'Light Pink'),
(4, 4, 'Orange'),
(5, 5, 'Light Green'),
(6, 6, 'Red'),
(7, 7, 'Yellow'),
(8, 8, 'Purple');

INSERT INTO "LookupDrinkIngredients" ("drink_id", "is_primary_ingredient", "is_key_additive", "ingredient_name", "amount", "unit")
VALUES
(1, True, False, 'Beetroot', 118.0, 'g'),
(1, False, True, 'Iron', 2.5, 'mg/ml'),
(1, False, False, 'Celery', 42.0, 'g'),
(1, False, False, 'Peeled Carrot', 65.0, 'g'),
(1, False, False, 'Cored Apple',  100.0, 'g'),
(1, False, False, 'Unpeeled Ginger', 3.0, 'g'),
(1, False, False, 'Lemon Juice', 10.87, 'g'),
(1, False, False, 'Cinnamon Powder', 0.03, 'g'),
(1, False, False, 'Matcha', 0.188, 'g'),
(2, True, False, 'Unpeeled Cucumber', 182.0, 'g'),
(2, False, True, 'Zinc', 25.0, 'mg'),
(2, False, False, 'Spinach', 75.0, 'g'),
(2, False, False, 'Celery', 70.0, 'g'),
(2, False, False, 'Unpeeled, Cored Granny Smith Apple', 50.0, 'g'),
(2, False, False, 'Unpeeled Ginger', 3.25, 'g'),
(2, False, False, 'Lemon Juice', 22.9, 'g'),
(2, False, False, 'Bee Pollen', 0.198, 'g'),
(3, True, False, 'Strawberry', 205.0, 'g'),
(3, False, True, 'Folic Acid', 400.0, 'mcg'),
(3, False, False, 'Unpeeled Cored Granny Smith Apple', 100.0, 'g'),
(3, False, False, 'Lemon Juice', 22.9, 'g'),
(3, False, False, 'Peeled Mango', 150.0, 'g'),
(4, True, False, 'Fresh Unpeeled Turmeric', 60.0, 'g'),
(4, False, True, 'Vitamin D', 3000.0, 'IU'),
(4, False, True, 'Calcium', 1000.0, 'mg'),
(4, False, False, 'Unpeeled Ginger', 3.3, 'g'),
(4, False, False, 'Orange Juice', 90.0, 'g'),
(4, False, False, 'Kampot Black Peppercorn', 1.0, 'pinch'),
(4, False, False, 'Peeled Carrot', 150.0, 'g'),
(4, False, False, 'Honey', 1.0, 'tbsp'),
(4, False, False, 'Lemon Juice', 36.0, 'g'),
(5, True, False, 'Coconut Water', 100.0, 'ml'),
(5, True, False, 'Avocado', 60.0, 'g'),
(5, False, True, 'Fish Oil', 1600.0, 'mg'),
(5, False, False, 'Banana', 60.0, 'g'),
(5, False, False, 'Matcha', 0.188, 'g'),
(5, False, False, 'Peeled, Cored Pear', 66.0, 'g'),
(5, False, False, 'Lemon', 55.0, 'g'),
(6, True, False, 'Peeled Watermelon', 80.0, 'g'),
(6, False, True, 'Vitamin B-12', 1000.0, 'mcg'),
(6, False, False, 'Strawberry', 80.0, 'g'),
(6, False, False, 'Red Pepper Flesh', 60.0, 'g'),
(6, False, False, 'Unpeeled, Cored Granny Smith Apple', 42.0, 'g'),
(6, False, False, 'Lemon Juice', 20.0, 'g'),
(6, False, False, 'Unpeeled, Cored Pear', 78.0, 'g'),
(7, True, False, 'Peeled Pineapple', 150.0, 'g'),
(7, False, True, 'Magnesium Citrate', 350.0, 'mg'),
(7, False, True, 'Protein', 0.0, 'g'),
(7, False, False, 'Mango Flesh', 92.0, 'g'),
(7, False, False, 'Lemon Juice', 13.0, 'g'),
(7, False, False, 'Orange Juice', 50.0, 'g'),
(7, False, False, 'Banana Flesh', 20.0, 'g'),
(8, True, False, 'Blueberry', 125.0, 'g'),
(8, False, True, 'NAD+', 300.0, 'mg'),
(8, False, True, 'Ubiquinol', 100.0, 'mg'),
(8, False, False, 'Pomegranate Seed', 100.0, 'g'),
(8, False, False, 'Banana Flesh', 35.0, 'g'),
(8, False, False, 'Unpeeled, Cored Granny Smith Apple', 57.0, 'g');

