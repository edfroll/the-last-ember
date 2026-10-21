# as the healer; the hearth interaction is the caller's context only through #i: place relative to the hearth via the bonfire record
execute unless function last_ember:bonfire/cauldron_free run return run title @s actionbar {"text":"Над огнём уже стоит котёл","color":"gray"}
item replace entity @s weapon.mainhand with minecraft:air
function last_ember:bonfire/cauldron_put_m with storage last_ember:bt cur
playsound minecraft:block.metal.place block @a[distance=..16] ~ ~ ~ 1 0.9
