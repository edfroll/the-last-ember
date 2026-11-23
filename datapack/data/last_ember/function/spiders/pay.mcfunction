# T-032: as a player of the fight that killed the Mistress (now or when he comes back): 2 Trophies of the Dol (T-029: no free slot - at the feet)
function last_ember:give/free
execute if score #free le.gv matches 1.. run loot give @s loot last_ember:contract/trophy_r1
execute if score #free le.gv matches 1.. run loot give @s loot last_ember:contract/trophy_r1
execute if score #free le.gv matches 0 at @s run loot spawn ~ ~ ~ loot last_ember:contract/trophy_r1
execute if score #free le.gv matches 0 at @s run loot spawn ~ ~ ~ loot last_ember:contract/trophy_r1
tag @s remove le.sppart
scoreboard players add #paid le.sp 1
