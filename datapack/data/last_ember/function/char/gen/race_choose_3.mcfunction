# as a player: picks Гномы
scoreboard players set @s le.race 3
function last_ember:char/gen/race_untag
tag @s add le.race.dwarf
function last_ember:char/gen/race_apply_3
effect give @s minecraft:instant_health 1 10 true
particle minecraft:totem_of_undying -22.5 61 24.5 0.6 2 0.6 0.1 40
playsound minecraft:block.beacon.activate player @s -15.5 57 24.5 1 1.3
tellraw @s {"text":"Ты — Гномы.","color":"gold"}
function last_ember:char/effects
function last_ember:char/open_hall
