# T-007: called from last_ember:load. keep_inventory: nothing drops by itself, the datapack decides what stays and what goes to the trail.
gamerule keep_inventory true
scoreboard objectives add le.deaths deathCount
scoreboard objectives add le.ash dummy
scoreboard objectives add le.tid dummy
scoreboard objectives add le.uid dummy
execute unless data storage last_ember:ash next run data merge storage last_ember:ash {next:1,t:{},urns:{}}
schedule function last_ember:death/loop 1t replace
schedule function last_ember:ash/slow_loop 10t replace
