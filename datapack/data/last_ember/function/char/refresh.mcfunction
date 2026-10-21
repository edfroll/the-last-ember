# as a player with a people (every second): modifiers and permanent effects are re-applied when they are gone
# (after death or relog): the probe is the modifier last_ember:race_scale (value 0 for people of normal height)
execute unless score @s le.swcd matches -2147483648..2147483647 run scoreboard players set @s le.swcd 0
execute store success score #pr le.e run attribute @s minecraft:scale modifier value get last_ember:race_scale
execute if score #pr le.e matches 0 run function last_ember:char/reapply
execute if score @s le.class matches 1.. store success score #pc le.e run attribute @s minecraft:luck modifier value get last_ember:class_mark
execute if score @s le.class matches 1.. if score #pc le.e matches 0 run function last_ember:char/gen/class_apply
function last_ember:char/effects
