# macro m: the ring goes back to the inventory with a line over the hotbar
$title @s actionbar {"text":"$(m)","color":"gray"}
item replace entity @s armor.head with minecraft:air
function last_ember:ring/give
playsound minecraft:block.note_block.basedrum player @s ~ ~ ~ 0.6 0.6
