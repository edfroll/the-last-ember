# as a player: a trap is about to hurt him: with 4.5 hearts or less a short strong resistance keeps him above one heart (a trap deals at most 8 points; above 9 points of health nothing is needed)
execute store result score #hp le.tr run data get entity @s Health
execute if score #hp le.tr matches ..9 run effect give @s minecraft:resistance 6 3 true
