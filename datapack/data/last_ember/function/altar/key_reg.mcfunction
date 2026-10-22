# macro id ch name
$execute unless data storage last_ember:keys k.$(id) run data modify storage last_ember:keys k.$(id) set value {gen:1,st:0,got:0b,it:0b,pend:0b}
$data modify storage last_ember:keys meta.$(id) set value {name:"$(name)",ch:$(ch)}
