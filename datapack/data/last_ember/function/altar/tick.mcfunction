function last_ember:altar/gen/event_tick
execute as @a[tag=le.carrier] at @s run function last_ember:altar/ember_hands
schedule function last_ember:altar/tick 1t replace
