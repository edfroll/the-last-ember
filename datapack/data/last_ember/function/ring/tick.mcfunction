# every tick (char/loop): who puts the ring on, who wears it
execute as @a[tag=le.race.halfling,tag=!le.ringon] if items entity @s armor.head *[minecraft:custom_data~{le_ring:1b}] at @s run function last_ember:ring/don
execute as @a[tag=!le.race.halfling] if items entity @s armor.head *[minecraft:custom_data~{le_ring:1b}] at @s run function last_ember:ring/refuse {m:"Кольцо не для тебя"}
execute as @a[tag=le.ringon] at @s run function last_ember:ring/on_tick
