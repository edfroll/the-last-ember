# the selected hotbar item stays with the player, unless it is a container holding items (shulker box, bundle) -- T-007 review
$execute if data storage last_ember:dt inv[{Slot:$(sel)b}].components."minecraft:container"[0] run return 0
$execute if data storage last_ember:dt inv[{Slot:$(sel)b}].components."minecraft:bundle_contents"[0] run return 0
$data remove storage last_ember:dt inv[{Slot:$(sel)b}]
