# as a player: picks Полурослики
scoreboard players set @s le.race 4
function last_ember:char/gen/race_untag
tag @s add le.race.halfling
function last_ember:char/gen/race_apply_4
effect give @s minecraft:instant_health 1 10 true
particle minecraft:totem_of_undying 17.4 61 41.4 0.6 2 0.6 0.1 40
playsound minecraft:block.beacon.activate player @s 12.5 57 36.5 1 1.3
tellraw @s {"text":"Ты — Полурослики.","color":"gold"}
function last_ember:char/effects
function last_ember:char/open_hall
