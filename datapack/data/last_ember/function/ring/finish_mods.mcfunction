# one tick after the ring was put on: the armor really is off, the difference of the attributes = the protection of the pieces that went into the storage
scoreboard players set @s le.rpend 0
execute store result score #a1 le.e run attribute @s minecraft:armor get 1000
execute store result score #t1 le.e run attribute @s minecraft:armor_toughness get 1000
execute store result score #k1 le.e run attribute @s minecraft:knockback_resistance get 1000
scoreboard players operation #a0 le.e = @s le.ra0
scoreboard players operation #t0 le.e = @s le.rt0
scoreboard players operation #k0 le.e = @s le.rk0
scoreboard players operation #a0 le.e -= #a1 le.e
scoreboard players operation #t0 le.e -= #t1 le.e
scoreboard players operation #k0 le.e -= #k1 le.e
execute store result storage last_ember:ring mod.a double 0.001 run scoreboard players get #a0 le.e
execute store result storage last_ember:ring mod.t double 0.001 run scoreboard players get #t0 le.e
execute store result storage last_ember:ring mod.k double 0.001 run scoreboard players get #k0 le.e
function last_ember:ring/mods_m with storage last_ember:ring mod
