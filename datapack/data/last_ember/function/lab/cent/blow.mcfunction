# as the player who punched a hit box: the damage of his blow (x100 in #dm) -> storage cd.d; Fire Aspect -> #fa
# vanilla: (weapon damage x (0.2 + 0.8 c^2) + enchantment bonus x c) x 1.5 when critical; c = the charge of the cooldown (0..1)
execute store result score #dm le.l run attribute @s minecraft:attack_damage get 100
execute store result score #sh le.l run data get entity @s SelectedItem.components."minecraft:enchantments"."minecraft:sharpness"
execute store result score #ba le.l run data get entity @s SelectedItem.components."minecraft:enchantments"."minecraft:bane_of_arthropods"
execute store result score #fa le.l run data get entity @s SelectedItem.components."minecraft:enchantments"."minecraft:fire_aspect"
scoreboard players set #eb le.l 0
execute if score #sh le.l matches 1.. run scoreboard players operation #eb le.l = #sh le.l
execute if score #sh le.l matches 1.. run scoreboard players operation #eb le.l *= #50 le.l
execute if score #sh le.l matches 1.. run scoreboard players add #eb le.l 50
scoreboard players operation #ba le.l *= #250 le.l
scoreboard players operation #eb le.l += #ba le.l
# the charge: ticks since his last blow on a box x attack speed / 20 (only the blows on boxes are seen: a swing at the air in between does not count)
execute store result score #sp le.l run attribute @s minecraft:attack_speed get 100
scoreboard players operation #c le.l = #gt le.l
scoreboard players operation #c le.l -= @s le.lcbt
execute unless score @s le.lcbt matches -2147483648.. run scoreboard players set #c le.l 100
scoreboard players operation @s le.lcbt = #gt le.l
scoreboard players operation #c le.l *= #sp le.l
scoreboard players operation #c le.l /= #20 le.l
execute if score #c le.l matches 101.. run scoreboard players set #c le.l 100
execute if score #c le.l matches ..-1 run scoreboard players set #c le.l 100
# x (20 + 80 c^2)/100 and the bonus x c
scoreboard players operation #m le.l = #c le.l
scoreboard players operation #m le.l *= #c le.l
scoreboard players operation #m le.l *= #80 le.l
scoreboard players operation #m le.l /= #10000 le.l
scoreboard players add #m le.l 20
scoreboard players operation #dm le.l *= #m le.l
scoreboard players operation #dm le.l /= #100 le.l
scoreboard players operation #eb le.l *= #c le.l
scoreboard players operation #eb le.l /= #100 le.l
scoreboard players operation #dm le.l += #eb le.l
execute if score #c le.l matches 90.. if predicate last_ember:lab/falling run scoreboard players operation #dm le.l *= #3 le.l
execute if score #c le.l matches 90.. if predicate last_ember:lab/falling run scoreboard players operation #dm le.l /= #2 le.l
execute if score #c le.l matches 90.. if predicate last_ember:lab/falling at @s run particle minecraft:crit ~ ~1 ~ 0.4 0.4 0.4 0.3 12
execute store result storage last_ember:lab cd.d float 0.01 run scoreboard players get #dm le.l
