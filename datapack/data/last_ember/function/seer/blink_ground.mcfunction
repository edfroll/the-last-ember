# going down from the block under the feet: #gr 1 = something to stand on (also water), -1 = lava, 0 = void (40 blocks of air)
execute if block ~ ~ ~ minecraft:lava run return run scoreboard players set #gr le.e -1
execute unless block ~ ~ ~ #last_ember:blink_pass run return run scoreboard players set #gr le.e 1
scoreboard players remove #g le.e 1
execute if score #g le.e matches 1.. positioned ~ ~-1 ~ run function last_ember:seer/blink_ground
