# resolved player name (no NBT holds it): a set_name item modifier run as the player, read back from a temporary display
summon minecraft:item_display ~ -1000 ~ {Tags:["le.nm"],item:{id:"minecraft:stone",count:1}}
item modify entity @e[type=minecraft:item_display,tag=le.nm,limit=1] contents last_ember:owner_name
data modify storage last_ember:dt rec.name set from entity @e[type=minecraft:item_display,tag=le.nm,limit=1] item.components."minecraft:custom_name".text
kill @e[type=minecraft:item_display,tag=le.nm]
