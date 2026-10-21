# macro urn: candles / sparks on when something is stored; plate shows the names. Works only while the urn chunk is loaded.
$data modify storage last_ember:dt u set from storage last_ember:ash urns.$(urn)
execute unless data storage last_ember:dt u.pos run return 0
execute store result score #u le.e run data get storage last_ember:dt u.n
data modify storage last_ember:dt pt set value [{text:"Утраченное\n",color:"gold"}]
data modify storage last_ember:dt nm set from storage last_ember:dt u.names
function last_ember:urn/plate_names
scoreboard players set #lit le.e 0
execute if data storage last_ember:dt u.trails[0] run scoreboard players set #lit le.e 1
function last_ember:urn/refresh_here with storage last_ember:dt u.pos
