# the death: it bursts and spreads into a puddle; a big one throws out two small ones; the puddle soaks away
execute if score @s le.lt matches 1 run function last_ember:lab/s/womb_death
execute if score @s le.lt matches 1 run function last_ember:lab/womb/shape {s:"splat",d:8}
execute if score @s le.lt matches 1..10 run particle minecraft:item_slime ~ ~0.4 ~ 0.8 0.3 0.8 0.1 6
execute if score @s le.lt matches 1..10 run particle minecraft:block{block_state:"minecraft:mud"} ~ ~0.2 ~ 0.9 0.1 0.9 0 4
execute if score @s le.lt matches 10 run function last_ember:lab/s/womb_death2
execute if score @s le.lt matches 12 if entity @s[tag=!le.lw_small] run function last_ember:lab/womb/spawn_small
execute if score @s le.lt matches 12 if entity @s[tag=!le.lw_small] run function last_ember:lab/womb/spawn_small
execute if score @s le.lt matches 25 run function last_ember:lab/womb/shape {s:"gone",d:20}
execute if score @s le.lt matches 45.. run function last_ember:lab/remove
