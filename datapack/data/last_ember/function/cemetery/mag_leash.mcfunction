# T-027: nobody living in the hall for 10 s: the Magister lies down again (full health next time), his spirits go
execute as @e[type=minecraft:skeleton,tag=le.cmag] at @s run particle minecraft:soul ~ ~1 ~ 0.4 0.8 0.4 0.03 30 force
execute as @e[type=minecraft:skeleton,tag=le.cmag] at @s run tp @s ~ -400 ~
kill @e[type=minecraft:skeleton,tag=le.cmag]
execute as @e[tag=le.cspirit] at @s run function last_ember:cemetery/spirit_gone
scoreboard players set #mg le.cem 0
scoreboard players set #ml le.cem 0
scoreboard players set #mh le.cem 0
