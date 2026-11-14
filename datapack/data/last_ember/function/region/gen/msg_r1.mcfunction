# generated: as a player: the message of the fade of r1 when he is in the region
function last_ember:elite/gen/region
execute if score #rg le.el matches 1 run title @s actionbar {"text":"Костры Дола гаснут.","color":"gold"}
execute if score #rg le.el matches 1 run playsound minecraft:block.fire.extinguish ambient @s ~ ~ ~ 0.6 0.5
