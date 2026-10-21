# as a player: picks Люди Долин
scoreboard players set @s le.race 1
function last_ember:char/gen/race_untag
tag @s add le.race.human
function last_ember:char/gen/race_apply_1
effect give @s minecraft:instant_health 1 10 true
particle minecraft:totem_of_undying 17.4 61 7.6 0.6 2 0.6 0.1 40
playsound minecraft:block.beacon.activate player @s 12.5 57 12.5 1 1.3
tellraw @s {"text":"Ты — Люди Долин.","color":"gold"}
function last_ember:char/effects
function last_ember:char/open_hall
