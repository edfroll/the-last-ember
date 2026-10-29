# the tree comes alive: bark cracks, it shakes, the branches come down as arms, a roar
function last_ember:lab/turn
scoreboard players add @s le.lt 1
execute if score @s le.lt matches 1 run playsound last_ember:creature.leshen.mv_wood_stress hostile @a ~ ~ ~ 2 0.7
execute if score @s le.lt matches 1..24 run particle minecraft:block{block_state:"minecraft:oak_log"} ~ ~2.5 ~ 0.6 1.2 0.6 0 3
execute if score @s le.lt matches 1..24 run particle minecraft:falling_spore_blossom ~ ~4 ~ 1.5 0.5 1.5 0 2
execute if score @s le.lt matches 2 run function last_ember:lab/rig_pose {r:"leshy",p:"tree_shake",d:3}
execute if score @s le.lt matches 6 run function last_ember:lab/rig_pose {r:"leshy",p:"tree",d:3}
execute if score @s le.lt matches 10 run function last_ember:lab/rig_pose {r:"leshy",p:"tree_shake",d:3}
execute if score @s le.lt matches 12 run playsound last_ember:creature.leshen.crow_call_double_custom hostile @a ~ ~4 ~ 2 1
execute if score @s le.lt matches 14 run function last_ember:lab/rig_pose {r:"leshy",p:"rise2",d:10}
execute if score @s le.lt matches 22 run playsound last_ember:creature.leshen.vo_taunt_scream hostile @a ~ ~ ~ 2 1
execute if score @s le.lt matches 26 run function last_ember:lab/rig_pose {r:"leshy",p:"idle0",d:10}
execute if score @s le.lt matches 36 run function last_ember:lab/awake
return 1
