# Register one bonfire and build it as soon as its chunk is loaded (macro: i id dim d x y z rx ry rz kind region eternal lit).
# Does nothing if already registered. Usable by hand while standing near:
#   function last_ember:bonfire/place {i:7,id:"r1_mill",dim:"minecraft:overworld",d:0,x:..,y:..,z:..,rx:..,ry:..,rz:..,kind:"normal",region:"r1",eternal:0,lit:0}
$execute if data storage last_ember:bonfires by.b$(i) run return 0
$data modify storage last_ember:bonfires by.b$(i) set value {i:$(i),id:"$(id)",dim:"$(dim)",d:$(d),x:$(x),y:$(y),z:$(z),rx:$(rx),ry:$(ry),rz:$(rz),kind:"$(kind)",region:"$(region)",eternal:$(eternal)b,state:0,built:0b}
$execute in $(dim) if loaded $(x) $(y) $(z) positioned $(x) $(y) $(z) run function last_ember:bonfire/build_now {i:$(i)}
