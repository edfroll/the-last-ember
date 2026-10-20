# from the carrier's eyes in 0.25 steps up to ~6 blocks: the first container block looked at loses its Ember copies
execute if items block ~ ~ ~ container.* *[minecraft:custom_data~{le_ember:1b}] run return run function last_ember:ember/strip_block
scoreboard players add #rn le.e 1
execute if score #rn le.e matches 25.. run return 0
execute positioned ^ ^ ^0.25 run function last_ember:ember/ray
