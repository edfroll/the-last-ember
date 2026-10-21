# as/at the clicked urn interaction: every stored trail -> the clicker; what does not fit -> the bowl
data remove entity @s interaction
execute store result storage last_ember:dt o.n int 1 run scoreboard players get @s le.uid
function last_ember:urn/collect_m with storage last_ember:dt o
