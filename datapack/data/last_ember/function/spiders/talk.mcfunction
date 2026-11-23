# T-032: advancement reward: a player right-clicked Toivo: in the thicket - his first window (each player once: le.sptk), then the
# later one; the first talk of anybody calls the quest's hook (T-031: q 0/1 -> 2) and lets him go home; at home - his window there
advancement revoke @s only last_ember:spiders/talk
scoreboard players enable @s le.sptrig
execute if score #toivo le.sp matches 2 run scoreboard players set @s le.spwin 4
execute if score #toivo le.sp matches 2 run return run dialog show @s last_ember:spiders/toivo_belfry
execute unless score #toivo le.sp matches 1 run return 0
execute if score #talked le.sp matches 0 run function last_ember:heather/hook/hunter_saved
scoreboard players set #talked le.sp 1
execute if entity @s[tag=le.sptk] run scoreboard players set @s le.spwin 3
execute if entity @s[tag=le.sptk] run return run dialog show @s last_ember:spiders/toivo_later
tag @s add le.sptk
scoreboard players set @s le.spwin 1
dialog show @s last_ember:spiders/toivo_first
