# the number of chapters changed: tiers, the lore of the Ember
function last_ember:altar/tier_sync
scoreboard players operation #t le.alt = #chapters le.alt
execute if score #t le.alt matches 7.. run scoreboard players set #t le.alt 6
execute store result storage last_ember:altar t.n int 1 run scoreboard players get #t le.alt
execute as @a[tag=le.carrier] run function last_ember:ember/gen/relore with storage last_ember:altar t
