# T-032: advancement reward: a player killed the Mistress
advancement revoke @s only last_ember:spiders/boss_killed
tag @s add le.sppart
scoreboard players operation @s le.spfight = #fight le.sp
function last_ember:spiders/boss_dead
