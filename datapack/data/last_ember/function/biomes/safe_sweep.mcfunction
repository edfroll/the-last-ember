# T-006: safe biomes (Refuge, Mushroom Grove, Early Winter) hold no monsters. natural_mob_spawns is empty there, but phantoms
# (their own vanilla spawner) and mobs walking in from the Vale are removed here, once a second, without drops.
execute as @e[type=#last_ember:monsters,tag=!le.keep] at @s if biome ~ ~ ~ #last_ember:safe run tp @s ~ -1000 ~
# T-023: pending fades of the chapters (biomes/gen/fade_<chapter>, unfade_<chapter>)
function last_ember:biomes/gen/sync
schedule function last_ember:biomes/safe_sweep 20t replace
