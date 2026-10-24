# the scolopendra rears up on its hind part (le.lfr counts 34 ticks down): it faces the prey and freezes, the front of the body rises in an arc,
# the head hangs high over the prey with the claws wide open and screams; then it strikes down with its whole body (cent/rear)
scoreboard players set @s le.lfr 34
execute store result score @s le.llook run random value 220..320
rotate @s facing entity @p[gamemode=!spectator,gamemode=!creative] feet
rotate @s ~ 0
attribute @s minecraft:movement_speed modifier add last_ember:lab_hold -1 add_multiplied_total
