# as the hurt entity (at itself): poison I for 4 s (#oilp = 1) or fire for 4 s (#oilp = 0)
tag @s add le.oilvic
execute if score #oilp le.e matches 1 run effect give @s minecraft:poison 4 0
execute if score #oilp le.e matches 0 if entity @s[type=!minecraft:player] run data modify entity @s Fire set value 80s
execute if score #oilp le.e matches 0 if entity @s[type=minecraft:player] if block ~ ~ ~ minecraft:air run setblock ~ ~ ~ minecraft:fire
tag @s remove le.oilvic
