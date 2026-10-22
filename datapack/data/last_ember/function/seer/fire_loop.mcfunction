# every 10 ticks while some of our fire stands: 5 s old fire is put out (only if it is still fire)
execute as @e[type=marker,tag=le.sfire] if score #gt le.e >= @s le.ft at @s run function last_ember:seer/fire_end
execute if entity @e[type=marker,tag=le.sfire,limit=1] run schedule function last_ember:seer/fire_loop 10t replace
