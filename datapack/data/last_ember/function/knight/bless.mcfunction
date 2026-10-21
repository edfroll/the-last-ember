# as a knight: the Blessing of the bonfire
scoreboard players set @s le.bless 0
scoreboard players operation @s le.blday = #day le.e
tag @s add le.blesser
execute as @e[type=minecraft:interaction,tag=le.hearth,distance=..6,limit=1,sort=nearest] at @s run function last_ember:knight/bless_fx
execute as @a[tag=le.blesser,limit=1] at @s as @a[distance=..8] run function last_ember:knight/sate
execute unless items entity @s armor.head *[minecraft:custom_data~{le_cursed:1b}] run item modify entity @s armor.head last_ember:repair30
execute unless items entity @s armor.chest *[minecraft:custom_data~{le_cursed:1b}] run item modify entity @s armor.chest last_ember:repair30
execute unless items entity @s armor.legs *[minecraft:custom_data~{le_cursed:1b}] run item modify entity @s armor.legs last_ember:repair30
execute unless items entity @s armor.feet *[minecraft:custom_data~{le_cursed:1b}] run item modify entity @s armor.feet last_ember:repair30
execute unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_cursed:1b}] run item modify entity @s weapon.mainhand last_ember:repair30
tag @s remove le.blesser
