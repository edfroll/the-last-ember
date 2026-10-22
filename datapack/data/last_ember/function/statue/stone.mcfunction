# as a statue that goes back: stone again (no AI, no sound, cannot be hurt), the stats of the elite are gone, full health
function last_ember:elite/unmake
data modify entity @s NoAI set value 1b
data modify entity @s Invulnerable set value 1b
data modify entity @s Silent set value 1b
data modify entity @s Fire set value 0s
data remove entity @s CustomName
data modify entity @s CustomNameVisible set value 0b
effect clear @s
execute store result storage last_ember:statue hp float 1 run attribute @s minecraft:max_health get
data modify entity @s Health set from storage last_ember:statue hp
