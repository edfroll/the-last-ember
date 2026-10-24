# from under the ground: a rumble and cracks first, then it bursts up; whoever stands within 4 blocks is thrown up (wound/quake)
execute if entity @s[tag=le.cent] run function last_ember:lab/cent/tick
function last_ember:lab/turn
execute if score @s le.lt matches 1 run function last_ember:lab/s/fish_dig
execute if score @s le.lt matches 1..19 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~1.6 ~ 0.5 0.05 0.5 0 4
execute if score @s le.lt matches 8 run function last_ember:lab/s/fish_rumble
execute if score @s le.lt matches 20..23 run tp @s ~ ~0.375 ~
execute if score @s le.lt matches 20 run function last_ember:lab/s/fish_emerge
execute if score @s le.lt matches 20 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~1.6 ~ 1.0 0.4 1.0 0.2 60
execute if score @s le.lt matches 20 run particle minecraft:block{block_state:"minecraft:rooted_dirt"} ~ ~1.8 ~ 0.4 0.6 0.4 0.3 40
execute if score @s le.lt matches 20 positioned ~ ~1.5 ~ as @a[distance=..4,gamemode=!spectator,gamemode=!creative] run function last_ember:wound/quake
execute if score @s le.lt matches 24 run function last_ember:lab/s/fish_taunt
execute if score @s le.lt matches 24 store result score @s le.lfd run random value 160..260
execute if score @s le.lt matches 24 run function last_ember:lab/awake
