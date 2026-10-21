$execute as @a[distance=..8,tag=!le.healer_self,scores={le.hp=$(v)},limit=1] at @s run function last_ember:potion/amulet_hit
scoreboard players operation @s le.amcd = #gt le.e
scoreboard players set #cd le.e 1200
scoreboard players operation #td le.e = @s le.tier
scoreboard players operation #td le.e *= #100 le.e
scoreboard players operation #cd le.e -= #td le.e
scoreboard players operation @s le.amcd += #cd le.e
