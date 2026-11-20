# T-027: advancement reward: a player right-clicked the crypt door: with the key in the main hand it opens for good (the key is taken),
# without it a line
advancement revoke @s only last_ember:cemetery/door
execute if score #door le.cem matches 1 run return 0
execute unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_citem:"crypt_key"}] run return run title @s actionbar {"text":"Заперто. Ключ ушёл в землю.","color":"gray","italic":true}
item replace entity @s weapon.mainhand with minecraft:air
scoreboard players set #door le.cem 1
scoreboard players set #ks le.cem 2
execute if score #q le.cem matches ..2 run scoreboard players set #q le.cem 3
function last_ember:cemetery/gen/door_set
playsound minecraft:block.iron_door.open block @a[distance=..16] ~ ~ ~ 1 0.6
playsound minecraft:block.chain.break block @a[distance=..16] ~ ~ ~ 0.8 0.5
function last_ember:cemetery/save
