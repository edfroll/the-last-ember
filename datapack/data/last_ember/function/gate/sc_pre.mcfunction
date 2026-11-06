# as/at a player just before the teleport: his tame pets that follow him (not sitting, within 12) go with him; the light of the Ember
tag @s add le.scme
execute as @e[type=#last_ember:shortcut_pets,distance=..12] if function last_ember:gate/pet_follows run tag @s add le.scpet
execute if entity @s[tag=le.carrier] run function last_ember:altar/light_off
