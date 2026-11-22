# T-030: the Advisor's menu for @s: after chapter I the window "after", at night the night menu, else the day menu
execute if score #chapters le.alt matches 1.. run return run dialog show @s last_ember:grove/after
execute if predicate last_ember:grove/night run return run dialog show @s last_ember:grove/menu_night
dialog show @s last_ember:grove/menu_day
