# as a wearer: off, and the ring itself back into the inventory (death, a new session, a reset)
function last_ember:ring/off
execute if items entity @s armor.head *[minecraft:custom_data~{le_ring:1b}] run item replace entity @s armor.head with minecraft:air
function last_ember:ring/give
