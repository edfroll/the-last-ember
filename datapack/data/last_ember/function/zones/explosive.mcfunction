# as/at a primed TNT, TNT minecart or end crystal: within 8 blocks of a zone -> defused without an explosion
scoreboard players set #hit le.z 0
function last_ember:zones/locate
function last_ember:zones/run_t with storage last_ember:zt a
execute if score #hit le.z matches 1 run particle minecraft:smoke ~ ~0.5 ~ 0.2 0.2 0.2 0.02 20
execute if score #hit le.z matches 1 run playsound minecraft:block.fire.extinguish block @a[distance=..16] ~ ~ ~ 1 1
execute if score #hit le.z matches 1 if entity @s[type=minecraft:tnt] run kill @s
execute if score #hit le.z matches 1 run tp @s ~ -1000 ~
