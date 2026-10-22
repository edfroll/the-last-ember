# as the hurt entity (at itself): poison I for 4 s (#oilp = 1) or fire for 4 s (#oilp = 0)
tag @s add le.oilvic
scoreboard players set #oilhit le.e 1
execute if score #oilp le.e matches 1 run effect give @s minecraft:poison 4 0
execute if score #oilp le.e matches 0 if entity @s[type=!minecraft:player] run data modify entity @s Fire set value 80s
tag @s remove le.oilvic
