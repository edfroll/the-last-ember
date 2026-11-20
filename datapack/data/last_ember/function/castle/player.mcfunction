# T-028: as/at one player near the castle (every 5 ticks): the pass at bonfire 8, the trigger of the colossi, the rock without the pass
scoreboard players set #prot le.cas 0
execute if entity @a[tag=le.sealh,distance=..10] run scoreboard players set #prot le.cas 1
execute if score @s le.sb matches 8 if function last_ember:castle/gen/near_hearth8 run tag @s add le.cpass
scoreboard players set #in le.cas 0
execute if function last_ember:castle/gen/in_trigger run scoreboard players set #in le.cas 1
execute if score #in le.cas matches 0 if function last_ember:castle/gen/in_rock run scoreboard players set #in le.cas 2
execute if score #in le.cas matches 0 if entity @s[tag=le.cpass] run scoreboard players add @s le.co 1
execute if score #in le.cas matches 1.. run scoreboard players set @s le.co 0
execute if score @s le.co matches 20.. run tag @s remove le.cpass
execute if score #in le.cas matches 0 run return 0
execute if entity @s[tag=le.cpass] run return 0
execute if score #in le.cas matches 1 if score #prot le.cas matches 1 run return run function last_ember:castle/recognize
execute if score @s le.cg > #gt le.cas run return 0
function last_ember:castle/wake
