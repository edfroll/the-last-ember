# macro: as a freshly summoned monster of a contract
tag @s remove le.cnewm
$scoreboard players set @s le.cnum $(n)
$scoreboard players set @s le.cdmg $(dmg)
execute store result score @s le.chp run data get entity @s Health 10
function last_ember:lab/new
