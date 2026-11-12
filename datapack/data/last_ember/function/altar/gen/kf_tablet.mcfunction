# generated: as the valid key tablet that just landed on the floor: the player who threw it is its last holder
tag @s add le.kthr
execute if data entity @s Thrower run data modify storage last_ember:keys k.tablet.h set from entity @s Thrower
