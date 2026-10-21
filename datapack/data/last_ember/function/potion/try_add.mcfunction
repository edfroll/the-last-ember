# as the cauldron, #bit le.e = the value of the ingredient, storage last_ember:cauldron cur = the item: returns 1 when it is accepted
scoreboard players operation #t le.e = @s le.cmask
scoreboard players operation #t le.e /= #bit le.e
scoreboard players operation #t le.e %= #2 le.e
execute if score #t le.e matches 1 run return 0
execute if score #bit le.e matches 1048576 unless score @s le.cmask matches 0 run return 0
scoreboard players operation #old le.e = @s le.cmask
scoreboard players operation @s le.cmask += #bit le.e
function last_ember:potion/valid
execute if score #ok le.e matches 0 run scoreboard players operation @s le.cmask = #old le.e
execute if score #ok le.e matches 0 run return 0
execute if score #bit le.e matches 1048576 run function last_ember:potion/keep_pot
return 1
