# T-030: the Advisor's menu for @s: after chapter I the window "after", at night the night menu, else the day menu (le.awin: the last
# window shown to the player: 1 intro, 2 menu day, 3 menu night, 4 after, 5 circle, 12..17 the answers of the buttons 2..7)
execute if score #chapters le.alt matches 1.. run scoreboard players set @s le.awin 4
execute if score #chapters le.alt matches 1.. run return run dialog show @s last_ember:grove/after
execute if predicate last_ember:grove/night run scoreboard players set @s le.awin 3
execute if predicate last_ember:grove/night run return run dialog show @s last_ember:grove/menu_night
scoreboard players set @s le.awin 2
dialog show @s last_ember:grove/menu_day
