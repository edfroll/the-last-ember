# T-028: one tick of the flight (as the thrown player): straight from the start to the knock point plus an arc 10 blocks high; teleported
# every tick (the motion of a player cannot be set; a teleport also clears the fall), the end in the water of the knock zone
scoreboard players add @s le.cf 1
function last_ember:castle/gen/arc
scoreboard players operation #x le.cas = @s le.cex
scoreboard players operation #x le.cas -= @s le.csx
scoreboard players operation #x le.cas *= @s le.cf
scoreboard players operation #x le.cas /= #N le.cas
scoreboard players operation #x le.cas += @s le.csx
scoreboard players operation #y le.cas = @s le.cey
scoreboard players operation #y le.cas -= @s le.csy
scoreboard players operation #y le.cas *= @s le.cf
scoreboard players operation #y le.cas /= #N le.cas
scoreboard players operation #y le.cas += @s le.csy
scoreboard players operation #y le.cas += #arc le.cas
scoreboard players operation #z le.cas = @s le.cez
scoreboard players operation #z le.cas -= @s le.csz
scoreboard players operation #z le.cas *= @s le.cf
scoreboard players operation #z le.cas /= #N le.cas
scoreboard players operation #z le.cas += @s le.csz
execute store result storage last_ember:castle fly.x double 0.01 run scoreboard players get #x le.cas
execute store result storage last_ember:castle fly.y double 0.01 run scoreboard players get #y le.cas
execute store result storage last_ember:castle fly.z double 0.01 run scoreboard players get #z le.cas
execute in minecraft:overworld run function last_ember:castle/fly_tp with storage last_ember:castle fly
execute at @s run particle minecraft:small_gust ~ ~0.8 ~ 0.3 0.3 0.3 0 2 force @a[distance=..96]
execute if score @s le.cf >= #N le.cas run function last_ember:castle/land
