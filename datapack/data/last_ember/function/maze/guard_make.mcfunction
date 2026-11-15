# T-024: as a woken guard at itself: the stats of an elite (T-014, like the living statues of T-016), the name «Страж сада»
tag @s add le.statue
function last_ember:elite/make
data modify entity @s CustomName set value {"text":"Страж сада","color":"dark_red"}
data modify entity @s CustomNameVisible set value 1b
