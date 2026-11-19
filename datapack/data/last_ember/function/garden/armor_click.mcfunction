# T-025: advancement reward: a player right-clicked the stand of the Creaking armour. Asleep garden: a full set, once per player
# (tag le.creak_got; a player who comes later gets his own); awake: a line over the hotbar.
advancement revoke @s only last_ember:garden/armor
execute if score #asleep le.gd matches 0 run return run title @s actionbar {"text":"Броня спит вместе с садом.","color":"gray","italic":true}
execute if entity @s[tag=le.creak_got] run return run title @s actionbar {"text":"Свой комплект ты уже взял.","color":"gray","italic":true}
tag @s add le.creak_got
loot give @s loot last_ember:item/creaking_armor
playsound minecraft:item.armor.equip_leather player @s ~ ~ ~ 1 0.7
playsound minecraft:block.creaking_heart.idle block @s ~ ~ ~ 0.5 0.6
