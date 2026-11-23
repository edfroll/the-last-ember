# T-031: advancement reward: a player hurt a dead villager: the resting ones just hurt (HurtTime 10 this tick) wake
advancement revoke @s only last_ember:heather/hit
execute as @e[type=minecraft:zombie_villager,tag=le.hzr,distance=..64] if data entity @s {HurtTime:10s} run function last_ember:heather/wake
