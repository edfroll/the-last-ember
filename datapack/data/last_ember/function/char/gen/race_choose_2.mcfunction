# as a player: picks Эльфы
scoreboard players set @s le.race 2
function last_ember:char/gen/race_untag
tag @s add le.race.elf
function last_ember:char/gen/race_apply_2
effect give @s minecraft:instant_health 1 10 true
particle minecraft:totem_of_undying 23.5 61 24.5 0.6 2 0.6 0.1 40
playsound minecraft:block.beacon.activate player @s 16.5 57 24.5 1 1.3
tellraw @s {"text":"Ты — Эльфы.","color":"gold"}
function last_ember:char/effects
function last_ember:char/open_hall
