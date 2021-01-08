
delete from "LookupDrinkIngredients" 
			where idx >= 1;
alter sequence "LookupDrinkIngredients_idx_seq"
  restart with 1;

delete from "LookupDrinks" 
	where drink_id >= 1;
alter sequence "LookupDrinks_drink_id_seq"
	restart with 1;

delete from "LookupGoals" 
  where goal_id >= 1;
alter sequence "LookupGoals_goal_id_seq"
  restart with 1;

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
(1, true, false, 'Beetroot', 118.0, 'g'),
(1, false, true, 'Iron', 2.5, 'mg/ml'),
(1, false, false, 'Celery', 42.0, 'g'),
(1, false, false, 'Peeled Carrot', 65.0, 'g'),
(1, false, false, 'Cored Apple',  100.0, 'g'),
(1, false, false, 'Unpeeled Ginger', 3.0, 'g'),
(1, false, false, 'Lemon Juice', 10.87, 'g'),
(1, false, false, 'Cinnamon Powder', 0.03, 'g'),
(1, false, false, 'Matcha', 0.188, 'g'),
(2, true, false, 'Unpeeled Cucumber', 182.0, 'g'),
(2, false, true, 'Zinc', 25.0, 'mg'),
(2, false, false, 'Spinach', 75.0, 'g'),
(2, false, false, 'Celery', 70.0, 'g'),
(2, false, false, 'Unpeeled, Cored Granny Smith Apple', 50.0, 'g'),
(2, false, false, 'Unpeeled Ginger', 3.25, 'g'),
(2, false, false, 'Lemon Juice', 22.9, 'g'),
(2, false, false, 'Bee Pollen', 0.198, 'g'),
(3, true, false, 'Strawberry', 205.0, 'g'),
(3, false, true, 'Folic Acid', 400.0, 'mcg'),
(3, false, false, 'Unpeeled Cored Granny Smith Apple', 100.0, 'g'),
(3, false, false, 'Lemon Juice', 22.9, 'g'),
(3, false, false, 'Peeled Mango', 150.0, 'g'),
(4, true, false, 'Fresh Unpeeled Turmeric', 60.0, 'g'),
(4, false, true, 'Vitamin D', 3000.0, 'IU'),
(4, false, true, 'Calcium', 1000.0, 'mg'),
(4, false, false, 'Unpeeled Ginger', 3.3, 'g'),
(4, false, false, 'Orange Juice', 90.0, 'g'),
(4, false, false, 'Kampot Black Peppercorn', 1.0, 'pinch'),
(4, false, false, 'Peeled Carrot', 150.0, 'g'),
(4, false, false, 'Honey', 1.0, 'tbsp'),
(4, false, false, 'Lemon Juice', 36.0, 'g'),
(5, true, false, 'Coconut Water', 100.0, 'ml'),
(5, true, false, 'Avocado', 60.0, 'g'),
(5, false, true, 'Fish Oil', 1600.0, 'mg'),
(5, false, false, 'Banana', 60.0, 'g'),
(5, false, false, 'Matcha', 0.188, 'g'),
(5, false, false, 'Peeled, Cored Pear', 66.0, 'g'),
(5, false, false, 'Lemon', 55.0, 'g'),
(6, true, false, 'Peeled Watermelon', 80.0, 'g'),
(6, false, true, 'Vitamin B-12', 1000.0, 'mcg'),
(6, false, false, 'Strawberry', 80.0, 'g'),
(6, false, false, 'Red Pepper Flesh', 60.0, 'g'),
(6, false, false, 'Unpeeled, Cored Granny Smith Apple', 42.0, 'g'),
(6, false, false, 'Lemon Juice', 20.0, 'g'),
(6, false, false, 'Unpeeled, Cored Pear', 78.0, 'g'),
(7, true, false, 'Peeled Pineapple', 150.0, 'g'),
(7, false, true, 'Magnesium Citrate', 350.0, 'mg'),
(7, false, true, 'Protein', 0.0, 'g'),
(7, false, false, 'Mango Flesh', 92.0, 'g'),
(7, false, false, 'Lemon Juice', 13.0, 'g'),
(7, false, false, 'Orange Juice', 50.0, 'g'),
(7, false, false, 'Banana Flesh', 20.0, 'g'),
(8, true, false, 'Blueberry', 125.0, 'g'),
(8, false, true, 'NAD+', 300.0, 'mg'),
(8, false, true, 'Ubiquinol', 100.0, 'mg'),
(8, false, false, 'Pomegranate Seed', 100.0, 'g'),
(8, false, false, 'Banana Flesh', 35.0, 'g'),
(8, false, false, 'Unpeeled, Cored Granny Smith Apple', 57.0, 'g');

