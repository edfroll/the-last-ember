# as the cauldron: 1..3 (tier 0) .. 2..6 (tier 6) result vials
scoreboard players operation #lo le.e = @s le.ctier
scoreboard players operation #lo le.e /= #6 le.e
scoreboard players add #lo le.e 1
scoreboard players operation #hi le.e = @s le.ctier
scoreboard players operation #hi le.e /= #2 le.e
scoreboard players add #hi le.e 3
execute store result storage last_ember:pt lo int 1 run scoreboard players get #lo le.e
execute store result storage last_ember:pt hi int 1 run scoreboard players get #hi le.e
function last_ember:potion/emit_roll with storage last_ember:pt
function last_ember:potion/emit_loop
