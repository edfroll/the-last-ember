# generated: as the valid key drop_source that just landed on the floor: the player who threw it is its last holder
tag @s add le.kthr
execute if data entity @s Thrower run data modify storage last_ember:keys k.drop_source.h set from entity @s Thrower
