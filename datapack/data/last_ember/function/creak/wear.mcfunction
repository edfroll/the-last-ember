# T-025: the Stillness of the Creaking armour (all 4 pieces worn), every 5 ticks, as the wearer at himself: the nearest monster he looks
# at (angle <= 20 degrees, within 8 blocks, nothing solid between: #last_ember:gaze_pass) gets slowness III and weakness I for 1 s;
# elves: 12 blocks and 25 degrees. One target per wearer. Not bosses, giants, NPCs, creakings.
tag @s add le.cgz
scoreboard players set #cf le.gd 0
execute if entity @s[tag=le.race.elf] as @e[type=#last_ember:monsters,distance=..12.5,sort=nearest,limit=12,tag=!le.boss,tag=!le.giant,tag=!le.npc,type=!minecraft:creaking] run function last_ember:creak/try12
execute unless entity @s[tag=le.race.elf] as @e[type=#last_ember:monsters,distance=..8.5,sort=nearest,limit=12,tag=!le.boss,tag=!le.giant,tag=!le.npc,type=!minecraft:creaking] run function last_ember:creak/try8
tag @s remove le.cgz
