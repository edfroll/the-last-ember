# the floor of cem_pit_15 falls
execute in minecraft:overworld positioned 263 93 464 run playsound minecraft:entity.generic.explode block @a[distance=..20] ~ ~ ~ 0.8 0.6
execute in minecraft:overworld run summon minecraft:falling_block 263.5 93.5 464.5 {BlockState:"minecraft:soul_soil",Time:1,DropItem:0b,CancelDrop:1b,HurtEntities:0b,Tags:["le.trap_fb"]}
execute in minecraft:overworld run summon minecraft:falling_block 263.5 93.5 465.5 {BlockState:"minecraft:soul_soil",Time:1,DropItem:0b,CancelDrop:1b,HurtEntities:0b,Tags:["le.trap_fb"]}
execute in minecraft:overworld run fill 263 93 464 263 93 465 minecraft:air replace minecraft:soul_soil
