# T-032: advancement reward: a player hurt a resting elite spider: the ones just hurt (HurtTime 10 this tick) wake
advancement revoke @s only last_ember:spiders/hit
execute as @e[type=minecraft:spider,tag=le.sprest,distance=..64] if data entity @s {HurtTime:10s} run function last_ember:spiders/wake
