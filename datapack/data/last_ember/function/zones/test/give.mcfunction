# T-004 test items for @s (no metal: wood/stick): caretaker shovel (breaks only soul_soil), cauldron (placeable on a campfire), ladle (takes the cauldron back)
give @s minecraft:wooden_shovel[minecraft:custom_name={"text":"Лопата смотрителя (тест)","italic":false},minecraft:can_break={blocks:"minecraft:soul_soil"}] 1
give @s minecraft:cauldron[minecraft:can_place_on={blocks:"minecraft:campfire"}] 2
give @s minecraft:stick[minecraft:custom_name={"text":"Черпак знахаря (тест)","italic":false},minecraft:can_break={blocks:"minecraft:cauldron"}] 1
