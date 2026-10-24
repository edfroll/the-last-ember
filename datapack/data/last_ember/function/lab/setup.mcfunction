# T-018: called from last_ember:load. The monster lab: five samples (lab/<kind>/spawn), the row for Edward (lab/row), wounds (wound/*).
scoreboard objectives add le.l dummy
scoreboard objectives add le.ls dummy
scoreboard objectives add le.lt dummy
scoreboard objectives add le.lhp dummy
scoreboard objectives add le.lx dummy
scoreboard objectives add le.lz dummy
scoreboard objectives add le.lsp dummy
scoreboard objectives add le.lst dummy
scoreboard objectives add le.lid dummy
scoreboard objectives add le.lcd dummy
scoreboard objectives add le.lpc dummy
scoreboard objectives add le.lfd dummy
scoreboard objectives add le.lfr dummy
scoreboard objectives add le.lan dummy
scoreboard objectives add le.llook dummy
scoreboard objectives add le.lair dummy
scoreboard objectives add le.lsq dummy
scoreboard objectives add le.lfl dummy
scoreboard objectives add le.wrot dummy
scoreboard objectives add le.wbl dummy
scoreboard objectives add le.wbs dummy
scoreboard objectives add le.wmu dummy
scoreboard objectives add le.wrt dummy
scoreboard objectives add le.wqk dummy
scoreboard players set #-1 le.l -1
scoreboard players set #20 le.l 20
scoreboard players set #60 le.l 60
scoreboard players set #80 le.l 80
scoreboard players set #360 le.l 360
scoreboard players set #10 le.l 10
scoreboard players set #2 le.l 2
scoreboard players set #5 le.l 5
scoreboard players set #4 le.l 4
scoreboard players set #8 le.l 8
scoreboard players set #dormant le.l 0
# the sound variants of the womb and the silverfish (lab/voice, Edward listens): 1 by default
execute unless score #v_fish le.l matches 1..3 run scoreboard players set #v_fish le.l 1
execute unless score #v_womb le.l matches 1..3 run scoreboard players set #v_womb le.l 1
# the shapes of the womb blob (scale of the display): big = size 3 (1.6), small = size 2 (1.05)
data modify storage last_ember:lab womb set value {big:{stretch:[1.36f,2.08f,1.36f],squash:[2.08f,0.96f,2.08f],neutral:[1.6f,1.6f,1.6f],charge:[1.76f,1.36f,1.76f],splat:[3.2f,0.24f,3.2f],gone:[0f,0f,0f]},small:{stretch:[0.89f,1.37f,0.89f],squash:[1.37f,0.63f,1.37f],neutral:[1.05f,1.05f,1.05f],charge:[1.16f,0.89f,1.16f],splat:[2.1f,0.16f,2.1f],gone:[0f,0f,0f]}}
function last_ember:lab/gen/leshy_parts
schedule function last_ember:lab/tick 1t replace
