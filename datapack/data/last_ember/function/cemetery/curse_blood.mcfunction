# T-027: the Blood: 1 damage (magic), never under 6 health
execute store result score @s le.chp run data get entity @s Health
execute if score @s le.chp matches 7.. run damage @s 1 minecraft:magic
