# every 5 ticks: the properties of the Ember (from the carrier; the chapters done: 1 Light, 2 Warmth, 3 Call (on use), 4 Gaze, 5 Flame)
tag @a[tag=le.warm] remove le.warm
execute as @a[tag=le.carrier] at @s run function last_ember:altar/ember_tick
execute unless entity @a[tag=le.carrier] run function last_ember:altar/light_off
schedule function last_ember:altar/ember_loop 5t replace
