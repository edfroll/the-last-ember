# Runs on world load / reload.
scoreboard objectives add le.init dummy
scoreboard players set #loaded le.init 1
# T-001b: no wandering traders
gamerule spawn_wandering_traders false
# T-001b: metal-gear drop control for natural mobs
schedule function last_ember:mob_eq/scan 10t replace
