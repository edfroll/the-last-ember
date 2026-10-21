# as a healer, at himself, every 4 ticks: a partner within 8 below 6 health gets Resistance III 2 s + Absorption I 10 s; the cooldown 60 s (tier 0) .. 30 s (tier 6); the weakest first
execute unless score @s le.amcd = @s le.amcd run scoreboard players set @s le.amcd 0
execute if score #gt le.e < @s le.amcd run return 0
tag @s add le.healer_self
execute as @a[distance=..8,tag=!le.healer_self,gamemode=!spectator] store result score @s le.hp run data get entity @s Health
execute as @a[distance=..8,tag=!le.healer_self,scores={le.hp=1..5}] run scoreboard players set #any le.e 1
execute unless score #any le.e matches 1 run return run tag @s remove le.healer_self
scoreboard players set #any le.e 0
function last_ember:potion/amulet_pick
tag @s remove le.healer_self
