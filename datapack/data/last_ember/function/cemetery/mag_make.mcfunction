# T-027: as the summoned Magister: an elite (T-014: scale, damage, speed, armour, health x2.5 = 100), his own name
function last_ember:elite/make
data modify entity @s CustomName set value {text:"Магистр Ордена Ясеня",color:"dark_red",bold:true}
data modify entity @s CustomNameVisible set value 1b
data merge entity @s {drop_chances:{head:0.0f,chest:0.0f,legs:0.0f,feet:0.0f,mainhand:0.0f}}
