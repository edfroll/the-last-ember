# Every tick. Players: full check every 5 ticks; every tick only while someone glides/falls fast or an ender pearl is in flight.
scoreboard players add #t le.z 1
execute store result score #t5 le.z run scoreboard players get #t le.z
scoreboard players operation #t5 le.z %= #5 le.z
execute if score #t5 le.z matches 0 as @a[gamemode=!creative,gamemode=!spectator] at @s run function last_ember:zones/player
execute unless score #t5 le.z matches 0 if entity @e[type=minecraft:ender_pearl,limit=1] as @a[gamemode=!creative,gamemode=!spectator] at @s run function last_ember:zones/player
execute unless score #t5 le.z matches 0 as @a[gamemode=!creative,gamemode=!spectator,predicate=last_ember:zone_fast] at @s run function last_ember:zones/player
# explosives near zones are defused (falling-block restore dropped: 26.3 falling blocks are not reliably selectable, see T-004 report)
execute as @e[type=#last_ember:explosive] at @s run function last_ember:zones/explosive
execute if score #t5 le.z matches 0 store result score #t20 le.z run scoreboard players get #t le.z
execute if score #t5 le.z matches 0 run scoreboard players operation #t20 le.z %= #20 le.z
execute if score #t5 le.z matches 0 if score #t20 le.z matches 0 run function last_ember:zones/gen/nospawn
schedule function last_ember:zones/loop 1t replace
