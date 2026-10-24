# the death: it staggers, falls to its knees, falls on its face, lies, then crumbles into bark and moss
function last_ember:lab/turn
execute if score @s le.lt matches 1 run function last_ember:lab/leshy/pose {p:"die0",d:6}
execute if score @s le.lt matches 1 run playsound last_ember:creature.leshen.vo_death hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 9 run function last_ember:lab/leshy/pose {p:"die1",d:10}
execute if score @s le.lt matches 9 run playsound last_ember:creature.leshen.mv_wood_stress hostile @a ~ ~ ~ 1.4 1
execute if score @s le.lt matches 21 run function last_ember:lab/leshy/pose {p:"die2",d:8}
execute if score @s le.lt matches 29 run playsound last_ember:creature.leshen.mv_bodyfall hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 29 rotated as @s run particle minecraft:block{block_state:"minecraft:rooted_dirt"} ^ ^0.2 ^1.5 1.0 0.1 1.0 0 40
execute if score @s le.lt matches 60 run function last_ember:lab/leshy/pose {p:"die3",d:22}
execute if score @s le.lt matches 60 run playsound last_ember:creature.leshen.leshy_break hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 60..80 rotated as @s run particle minecraft:block{block_state:"minecraft:oak_log"} ^ ^0.4 ^1.4 0.6 0.2 1.0 0 6
execute if score @s le.lt matches 60..80 rotated as @s run particle minecraft:block{block_state:"minecraft:moss_block"} ^ ^0.4 ^1.4 0.6 0.2 1.0 0 3
execute if score @s le.lt matches 84.. run function last_ember:lab/remove
