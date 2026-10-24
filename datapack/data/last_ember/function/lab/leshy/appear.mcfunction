function last_ember:lab/turn
execute if score @s le.lt matches 1 run playsound last_ember:creature.leshen.crow_call_double_custom hostile @a ~ ~3 ~ 2.0 1
execute if score @s le.lt matches 8 run playsound last_ember:creature.leshen.vo_spawn hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 1..30 run particle minecraft:block{block_state:"minecraft:rooted_dirt"} ~ ~0.1 ~ 0.8 0.05 0.8 0 3
execute if score @s le.lt matches 30 run function last_ember:lab/leshy/pose {p:"rise1",d:20}
execute if score @s le.lt matches 30 run playsound last_ember:creature.leshen.mv_spawn hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 30..55 run particle minecraft:block{block_state:"minecraft:rooted_dirt"} ~ ~0.3 ~ 0.7 0.2 0.7 0.05 6
execute if score @s le.lt matches 30..55 run particle minecraft:block{block_state:"minecraft:moss_block"} ~ ~1 ~ 0.5 0.8 0.5 0 2
execute if score @s le.lt matches 50 run function last_ember:lab/leshy/pose {p:"rise2",d:10}
execute if score @s le.lt matches 50 run playsound last_ember:creature.leshen.mv_wood_stress hostile @a ~ ~ ~ 1.4 1
execute if score @s le.lt matches 62 run function last_ember:lab/leshy/pose {p:"idle0",d:10}
execute if score @s le.lt matches 62 run playsound last_ember:creature.leshen.vo_taunt_scream hostile @a ~ ~ ~ 2.0 1
execute if score @s le.lt matches 72 run function last_ember:lab/awake
