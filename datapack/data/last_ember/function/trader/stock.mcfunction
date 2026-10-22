# ADMIN/TEST, as a player: the remaining deals of a trader: function last_ember:trader/stock {id:"smith"}
tag @s add le.stk
$execute as @e[tag=le.tr_$(id),limit=1] run function last_ember:trader/show
tag @s remove le.stk
