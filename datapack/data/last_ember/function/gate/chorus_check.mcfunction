# T-022: each tick for 6 ticks after eating a chorus fruit: crossed a border axis outside an open gap (or hopped behind a closed gate) -> back
scoreboard players remove @s le.cht 1
execute if score @s le.cht matches ..0 run tag @s remove le.chorus
execute store result score @s le.cnx run data get entity @s Pos[0] 10
execute store result score @s le.cnz run data get entity @s Pos[2] 10
function last_ember:gate/gen/chorus
