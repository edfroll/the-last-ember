# T-030: advancement reward: a player right-clicked the Advisor: at the Circle his own window; the first talk of this player: the
# acquaintance; then the menu (after chapter I: the window "after")
advancement revoke @s only last_ember:grove/talk
scoreboard players enable @s le.atrig
execute unless score @s le.ametg = #met le.grv run tag @s remove le.amet
execute if score #cur le.grv matches 2 run scoreboard players set @s le.awin 5
execute if score #cur le.grv matches 2 run return run dialog show @s last_ember:grove/circle
execute unless entity @s[tag=le.amet] run return run function last_ember:grove/meet
function last_ember:grove/menu
