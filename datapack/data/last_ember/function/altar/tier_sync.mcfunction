# every second (unless #tiersync is 0 = tests): the tier of everybody = the chapters done (players who were offline get it when they come back)
execute if score #tiersync le.alt matches 0 run return 0
scoreboard players operation #t le.alt = #chapters le.alt
execute if score #t le.alt matches 7.. run scoreboard players set #t le.alt 6
execute as @a[scores={le.class=1..}] unless score @s le.tier = #t le.alt run function last_ember:altar/tier_set
