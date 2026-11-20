# the floor of cem_pit_16 falls
execute in minecraft:overworld positioned 273 96 489 run playsound minecraft:entity.generic.explode block @a[distance=..20] ~ ~ ~ 0.8 0.6
execute in minecraft:overworld run summon minecraft:falling_block 273.5 96.5 489.5 {BlockState:"minecraft:soul_soil",Time:1,DropItem:0b,CancelDrop:1b,HurtEntities:0b,Tags:["le.trap_fb"]}
execute in minecraft:overworld run summon minecraft:falling_block 273.5 96.5 490.5 {BlockState:"minecraft:soul_soil",Time:1,DropItem:0b,CancelDrop:1b,HurtEntities:0b,Tags:["le.trap_fb"]}
execute in minecraft:overworld run fill 273 96 489 273 96 490 minecraft:air replace minecraft:soul_soil
