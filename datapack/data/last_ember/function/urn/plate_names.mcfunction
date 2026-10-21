execute unless data storage last_ember:dt nm[0] run return 0
data modify storage last_ember:dt pt append value {text:"",color:"gray"}
data modify storage last_ember:dt pt[-1].text set from storage last_ember:dt nm[0].n
data modify storage last_ember:dt pt append value "\n"
data remove storage last_ember:dt nm[0]
function last_ember:urn/plate_names
