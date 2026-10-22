# as a halfling at himself: the ring is on the head -> the armor goes into the storage, its protection stays as modifiers, invisibility
execute if score #gt le.e < @s le.rcd run return run function last_ember:ring/refuse_cd
execute if data entity @s {FallFlying:1b} run return run function last_ember:ring/refuse {m:"Не в полёте"}
execute if items entity @s armor.chest minecraft:elytra if data entity @s {OnGround:0b} run return run function last_ember:ring/refuse {m:"Не в полёте"}
execute if data entity @s equipment.chest.components."minecraft:enchantments"."minecraft:binding_curse" run return run function last_ember:ring/refuse {m:"Что-то держит тебя в этом мире"}
execute if data entity @s equipment.legs.components."minecraft:enchantments"."minecraft:binding_curse" run return run function last_ember:ring/refuse {m:"Что-то держит тебя в этом мире"}
execute if data entity @s equipment.feet.components."minecraft:enchantments"."minecraft:binding_curse" run return run function last_ember:ring/refuse {m:"Что-то держит тебя в этом мире"}
function last_ember:ring/key
data modify storage last_ember:ring cur set value {}
data modify storage last_ember:ring cur.chest set from entity @s equipment.chest
data modify storage last_ember:ring cur.legs set from entity @s equipment.legs
data modify storage last_ember:ring cur.feet set from entity @s equipment.feet
execute store result score @s le.ra0 run attribute @s minecraft:armor get 1000
execute store result score @s le.rt0 run attribute @s minecraft:armor_toughness get 1000
execute store result score @s le.rk0 run attribute @s minecraft:knockback_resistance get 1000
function last_ember:ring/save_m with storage last_ember:ring u
item modify entity @s armor.head last_ember:ring_stash
item replace entity @s armor.chest with minecraft:air
item replace entity @s armor.legs with minecraft:air
item replace entity @s armor.feet with minecraft:air
# the attributes follow the empty slots on the next tick: the modifiers are set then (ring/finish_mods)
scoreboard players set @s le.rpend 2
tag @s add le.ringon
scoreboard players operation @s le.rt = #gt le.e
scoreboard players operation @s le.rlast = #gt le.e
effect give @s minecraft:invisibility 2 0 true
particle minecraft:smoke ~ ~1 ~ 0.2 0.5 0.2 0.02 20
playsound minecraft:entity.vex.ambient player @a[distance=..16,tag=!le.ringon] ~ ~ ~ 0.4 0.5
playsound minecraft:item.armor.equip_leather player @s ~ ~ ~ 0.3 0.6
