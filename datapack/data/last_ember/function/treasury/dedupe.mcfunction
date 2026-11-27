# T-034: as/at a decor display: another one at the very same spot (summoned again before the chunk's entities loaded): this one goes
tag @s add le.trself
execute if entity @e[type=minecraft:item_display,tag=le.tr_deco,tag=!le.trself,distance=..0.05] run kill @s
tag @s remove le.trself
