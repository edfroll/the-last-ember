scoreboard players remove @s le.lfr 1
execute if score @s le.lfr matches 13 run rotate @s ~38 ~-25
execute if score @s le.lfr matches 9 run rotate @s ~-70 ~30
execute if score @s le.lfr matches 5 run rotate @s ~45 ~-15
execute if score @s le.lfr matches 0 run attribute @s minecraft:movement_speed modifier remove last_ember:lab_hold
# out of the stillness it throws itself forward when the prey is in reach of a leap
execute if score @s le.lfr matches 0 if entity @a[distance=3.5..8,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/drowner/lunge
