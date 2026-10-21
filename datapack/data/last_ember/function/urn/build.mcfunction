# macro n urn variant x y z dim, executed at the urn anchor (centre of the podium, square level). Placeholder look per the card until the Architect's .nbt.
$data modify storage last_ember:ash urns.$(urn).built set value 1b
$data modify storage last_ember:ash urns.$(urn).n set value $(n)
$data modify storage last_ember:ash urns.$(urn).pos set value {x:$(x),y:$(y),z:$(z),dim:"$(dim)"}
$execute unless data storage last_ember:ash urns.$(urn).trails run data modify storage last_ember:ash urns.$(urn).trails set value []
$execute unless data storage last_ember:ash urns.$(urn).names run data modify storage last_ember:ash urns.$(urn).names set value []
$data modify storage last_ember:ash urn_ids.u$(n) set value "$(urn)"
$function last_ember:urn/gen/build_$(variant)
$scoreboard players set #u le.e $(n)
kill @e[type=minecraft:interaction,tag=le.urnclick,distance=..4]
kill @e[type=minecraft:text_display,tag=le.urn_plate,distance=..6]
summon minecraft:interaction ~ ~1 ~ {width:3.2f,height:5.5f,response:1b,Tags:["le.urnclick","le.urnnew"]}
summon minecraft:text_display ~ ~3.4 ~-3.3 {Tags:["le.urn_plate","le.urnnew"],billboard:"center",text:"",background:1140850688,line_width:120}
execute as @e[tag=le.urnnew,distance=..6] run scoreboard players operation @s le.uid = #u le.e
tag @e[tag=le.urnnew,distance=..6] remove le.urnnew
$function last_ember:urn/refresh {urn:"$(urn)"}
