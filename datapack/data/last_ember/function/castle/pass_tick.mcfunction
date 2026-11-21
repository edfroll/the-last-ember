# T-028: as/at a player with the pass (every 5 ticks): on the rock or in the trigger the count starts again, else +1; 20 (5 s) -> no pass
scoreboard players add @s le.co 1
execute if function last_ember:castle/gen/in_trigger run scoreboard players set @s le.co 0
execute if function last_ember:castle/gen/in_rock run scoreboard players set @s le.co 0
execute if score @s le.co matches 20.. run tag @s remove le.cpass
