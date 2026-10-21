$data modify storage last_ember:dt tr set from storage last_ember:ash urns.$(urn).trails
$data modify storage last_ember:ash urns.$(urn).trails set value []
$data modify storage last_ember:dt bowl set from storage last_ember:ash urns.$(urn).pos
$function last_ember:urn/bowl_pos with storage last_ember:ash urns.$(urn).pos
execute unless data storage last_ember:dt tr[0] run title @a[tag=le.clicker] actionbar {"text":"Урна пуста","color":"gray"}
execute as @a[tag=le.clicker,limit=1] at @s run function last_ember:urn/give_all
schedule function last_ember:ash/out_to_bowl 3t replace
$function last_ember:urn/refresh {urn:"$(urn)"}
