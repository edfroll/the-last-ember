scoreboard players set #wact le.e 1
scoreboard players set #wprev le.e 0
execute if predicate last_ember:raining run scoreboard players set #wprev le.e 1
execute if predicate last_ember:thundering run scoreboard players set #wprev le.e 2
execute unless score #wprev le.e matches 2 run weather thunder 1200
