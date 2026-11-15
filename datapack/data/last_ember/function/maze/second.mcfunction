# T-024: every second (in the overworld): what stands follows the state; the guards; the key on its pedestal; the heads
function last_ember:maze/gen/sync
function last_ember:maze/gen/guards_sec
execute if score #key le.mz matches 0 if loaded -150 112 -430 run function last_ember:maze/gen/key_build
execute if score #key le.mz matches 1 if loaded -150 112 -430 unless entity @e[type=minecraft:interaction,tag=le.mzkey,x=-150,y=112,z=-430,distance=..3] run function last_ember:maze/gen/key_build
