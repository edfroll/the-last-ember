# T-024: every 5 ticks: players in the maze (dead-end statues: gaze and heads), pending rebuilds, the shuffle every 45 s while somebody
# is inside, the guards, the roof; every second the sync of what stands with the state
schedule function last_ember:maze/loop 5t replace
execute store result score #gt le.mz run time query gametime
scoreboard players add #t le.mz 5
execute in minecraft:overworld store result score #inmz le.mz if entity @a[x=-211,y=103,z=-491,dx=121,dy=24,dz=121,gamemode=!spectator]
execute if score #inmz le.mz matches 1.. in minecraft:overworld as @a[x=-211,y=103,z=-491,dx=121,dy=24,dz=121,gamemode=!spectator] at @s run function last_ember:maze/player
execute in minecraft:overworld run function last_ember:maze/gen/pend
execute if score #inmz le.mz matches 1.. run scoreboard players add #shuf le.mz 5
execute if score #shuf le.mz matches 900.. in minecraft:overworld run function last_ember:maze/shuffle_auto
execute if score #key le.mz matches 2 in minecraft:overworld if entity @a[x=-150,y=112,z=-430,distance=..10,gamemode=!spectator] run function last_ember:maze/gen/wake_all
execute in minecraft:overworld run function last_ember:maze/gen/guards
execute in minecraft:overworld run function last_ember:maze/gen/roof
scoreboard players operation #t10 le.mz = #t le.mz
scoreboard players operation #t10 le.mz %= #20 le.mz
execute if score #t10 le.mz matches 0 in minecraft:overworld run function last_ember:maze/second
execute if score #t10 le.mz matches 10 in minecraft:overworld run function last_ember:maze/gen/heads
