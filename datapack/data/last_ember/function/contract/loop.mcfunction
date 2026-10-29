# every 5 ticks: the players in the cells of the contracts (clues, baits, ritual circles), twins, the take and choice buttons; every second the rest
execute store result score #gt le.ct run time query gametime
scoreboard players add #q le.ct 1
scoreboard players operation #half le.ct = #q le.ct
scoreboard players operation #half le.ct %= #2 le.ct
# (only while some contract is taken: #active from gen/sec)
execute if score #active le.ct matches 1.. as @a[gamemode=!spectator,gamemode=!creative] at @s run function last_ember:contract/locate
function last_ember:contract/gen/fast
execute as @a[scores={le.ctake=1..}] at @s run function last_ember:contract/take_trig
execute as @a[scores={le.choice=1..}] at @s run function last_ember:contract/choice_trig
scoreboard players add #sec le.ct 1
execute if score #sec le.ct matches 4.. run function last_ember:contract/second
schedule function last_ember:contract/loop 5t replace
