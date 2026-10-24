# for a second after the leap, on the ground: a small push toward the prey every 4 ticks, so the zombie walks at him at once
scoreboard players remove @s le.llook 1
execute if score #t4 le.l matches 0 if entity @s[nbt={OnGround:1b}] if entity @a[distance=1.5..12,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/drowner/push {f:0.22,y:0.0}
