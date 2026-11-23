# T-032: the third cut: the cocoon open (its template), Toivo falls out and sits by it; his bow goes (he took it)
function last_ember:spiders/gen/cocoon_open
scoreboard players set #toivo le.sp 1
data modify storage last_ember:spiders toivo set value 1
kill @e[type=minecraft:item_display,tag=le.spbow]
function last_ember:spiders/gen/toivo_thicket
execute as @e[type=minecraft:interaction,tag=le.sp_coc,limit=1] at @s run playsound minecraft:entity.player.hurt_sweet_berry_bush player @a[distance=..16] ~ ~1 ~ 1 0.8
execute as @e[type=minecraft:interaction,tag=le.sp_coc,limit=1] at @s run particle minecraft:block{block_state:"minecraft:cobweb"} ~ ~1.5 ~ 0.8 1 0.8 0 60
