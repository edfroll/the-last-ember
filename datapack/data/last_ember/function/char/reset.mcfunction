# TEST/ADMIN: as a player: no people, no class, no kit tag, no modifiers; back to the Cell. Usage: execute as <player> run function last_ember:char/reset
function last_ember:char/gen/race_strip
function last_ember:char/gen/class_strip
function last_ember:char/gen/race_untag
function last_ember:char/gen/class_untag
tag @s remove le.kit
tag @s remove le.cinit
scoreboard players set @s le.race 0
scoreboard players set @s le.class 0
scoreboard players reset @s le.pend
scoreboard players reset @s le.sb
effect clear @s minecraft:hero_of_the_village
effect clear @s minecraft:resistance
function last_ember:char/newcomer
