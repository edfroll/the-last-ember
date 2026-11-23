# T-031: advancement reward: a player right-clicked the ringer: the first talk of this player - the acquaintance, then the menu
advancement revoke @s only last_ember:heather/talk
scoreboard players enable @s le.htrig
playsound minecraft:entity.villager.ambient neutral @s ~ ~ ~ 0.5 0.7
execute unless score @s le.hmetg = #met le.hv run tag @s remove le.hmet
execute unless entity @s[tag=le.hmet] run return run function last_ember:heather/meet
function last_ember:heather/menu
