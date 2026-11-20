# T-027: advancement reward: a player right-clicked the seal in the sarcophagus: it goes to him (the current generation)
advancement revoke @s only last_ember:cemetery/seal
execute unless score #ss le.cem matches 1 run return 0
function last_ember:cemetery/give {key:"seal"}
scoreboard players set #ss le.cem 2
kill @e[type=minecraft:item_display,tag=le.csealdisp]
kill @e[type=minecraft:interaction,tag=le.cseal]
playsound minecraft:block.vault.open_shutter block @a[distance=..16] ~ ~ ~ 1 0.6
function last_ember:cemetery/save
