# as a player who has never been through the Hall: the Cell bed, no bonfire binding, the door opens in 5 s
tag @s add le.cinit
scoreboard players set @s le.race 0
scoreboard players set @s le.class 0
scoreboard players set @s le.tier 0
scoreboard players set @s le.swcd 0
scoreboard players reset @s le.sb
execute if score #autochar le.e matches 1 run return run function last_ember:char/auto
function last_ember:char/to_bed
