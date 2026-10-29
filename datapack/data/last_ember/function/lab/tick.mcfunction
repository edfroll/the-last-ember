# every tick: the lab samples and the wounded players; every second the loose parts are cleaned up
execute store result score #gt le.l run time query gametime
execute as @e[type=#last_ember:lab_bodies,tag=le.lab_body] at @s run function last_ember:lab/body
# the carrier hit through a segment stays marked for one tick: the oils (potion/oil_hit, an advancement reward) find it
tag @e[tag=le.chitv] remove le.chitv
execute as @e[type=minecraft:interaction,tag=le.cbox] if data entity @s attack run function last_ember:lab/cent/box_hit
execute as @a[tag=le.wound] at @s run function last_ember:wound/tick
scoreboard players add #sec le.l 1
execute if score #sec le.l matches 20.. run function last_ember:lab/second
schedule function last_ember:lab/tick 1t replace
