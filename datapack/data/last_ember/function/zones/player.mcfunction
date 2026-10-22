# as/at one player: inside any zone (+5 blocks reach margin) -> adventure; left all zones -> back to survival (only if we set adventure)
scoreboard players set #hit le.z 0
tag @s remove le.zf.no_spawn
tag @s remove le.zf.no_blink
tag @s remove le.zf.no_fire
tag @s remove le.zf.calm
tag @s remove le.zf.dungeon
function last_ember:zones/locate
function last_ember:zones/run_p with storage last_ember:zt a
execute if score #hit le.z matches 1 if entity @s[gamemode=survival] run function last_ember:zones/enter
execute if score #hit le.z matches 0 if entity @s[tag=le.zadv,gamemode=adventure] run function last_ember:zones/leave
execute if score #hit le.z matches 0 run tag @s remove le.zadv
