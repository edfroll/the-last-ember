# T-029 review: macro table, need: as/at a player: the loot of `table` into the inventory when `need` slots are free, else on the ground at the feet
# (LootCommand.playerGive only adds to the inventory: what does not fit is lost)
function last_ember:give/free
$execute if score #free le.gv matches $(need).. run return run loot give @s loot $(table)
$loot spawn ~ ~ ~ loot $(table)
scoreboard players add #dropped le.gv 1
