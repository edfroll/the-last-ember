scoreboard players set #sec le.l 0
# a part whose carrier is gone (killed by a command, unloaded apart from it) is removed
execute as @e[type=minecraft:item_display,tag=le.lab_part] unless function last_ember:lab/has_vehicle run kill @s
