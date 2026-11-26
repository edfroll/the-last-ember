# T-033: advancement reward: a player hurt a resting dead miner or Bran: those just hurt (HurtTime 10 this tick) wake
advancement revoke @s only last_ember:mines/hit
execute as @e[type=minecraft:zombie,tag=le.mnr,distance=..64] if data entity @s {HurtTime:10s} run function last_ember:mines/wake
