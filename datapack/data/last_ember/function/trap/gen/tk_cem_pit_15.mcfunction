# generated: one tick of cem_pit_15
scoreboard players add #cem_pit_15_t le.tr 1
execute if score #cem_pit_15_t le.tr matches 1 in minecraft:overworld positioned 263 93 464 run playsound minecraft:block.gravel.break block @a[distance=..16] ~ ~ ~ 1.2 0.5
execute if score #cem_pit_15_t le.tr matches 1 in minecraft:overworld positioned 263 93 464 run particle minecraft:block{block_state:"minecraft:soul_soil"} ~ ~1.1 ~ 0.5 0.1 1.0 0.05 12 force
execute if score #cem_pit_15_t le.tr matches 5 in minecraft:overworld positioned 263 93 464 run particle minecraft:block{block_state:"minecraft:soul_soil"} ~ ~1.1 ~ 0.5 0.1 1.0 0.05 12 force
execute if score #cem_pit_15_t le.tr matches 10 in minecraft:overworld positioned 263 93 464 run particle minecraft:block{block_state:"minecraft:soul_soil"} ~ ~1.1 ~ 0.5 0.1 1.0 0.05 12 force
execute if score #cem_pit_15_t le.tr matches 15 in minecraft:overworld positioned 263 93 464 run particle minecraft:block{block_state:"minecraft:soul_soil"} ~ ~1.1 ~ 0.5 0.1 1.0 0.05 12 force
execute if score #cem_pit_15_t le.tr matches 20 run function last_ember:trap/gen/drop_cem_pit_15
execute if score #cem_pit_15_t le.tr matches 45 run execute in minecraft:overworld run kill @e[type=minecraft:falling_block,tag=le.trap_fb]
execute if score #cem_pit_15_t le.tr matches 46.. if score #cem_pit_15_st le.tr matches 1 run scoreboard players set #cem_pit_15_st le.tr 3
# (the waiting state counts the ticks)
execute if score #cem_pit_15_t le.tr matches 1250.. if score #cem_pit_15_st le.tr matches 3 in minecraft:overworld unless entity @a[x=262,y=92,z=463,dx=2,dy=5,dz=3] run function last_ember:trap/gen/restore_cem_pit_15
