# as/at the cauldron interaction: water goes in with a bucket or a bottle (healer), only a sneaking healer takes the cauldron back
execute as @a[tag=le.clicker,limit=1] if function last_ember:potion/fill_try run return 0
# as/at the cauldron interaction: only a sneaking healer takes it back; others just get a hint
execute unless entity @a[tag=le.clicker,tag=le.class.healer,predicate=last_ember:sneaking] run return run title @a[tag=le.clicker] actionbar {"text":"Котёл знахаря: снять его может только знахарь (Shift+ПКМ)","color":"gray"}
execute if block ~ ~ ~ minecraft:cauldron run setblock ~ ~ ~ minecraft:air
execute if block ~ ~ ~ minecraft:water_cauldron run setblock ~ ~ ~ minecraft:air
# T-029 review: the cauldron is one of a kind: with a full inventory it lands at the healer's feet
execute if entity @s[tag=le.pot_old] as @a[tag=le.clicker,limit=1] at @s run function last_ember:give/loot {table:"last_ember:item/old_cauldron",need:1}
execute unless entity @s[tag=le.pot_old] as @a[tag=le.clicker,limit=1] run function last_ember:give/free
execute unless entity @s[tag=le.pot_old] if score #free le.gv matches 1.. as @a[tag=le.clicker,limit=1] run give @s minecraft:cauldron[minecraft:custom_data={le_cauldron:1b,le_keep:1b},minecraft:custom_name={"text":"Котёл знахаря","italic":false,"color":"green"}] 1
execute unless entity @s[tag=le.pot_old] if score #free le.gv matches 0 as @a[tag=le.clicker,limit=1] at @s run summon minecraft:item ~ ~0.3 ~ {PickupDelay:10s,Item:{id:"minecraft:cauldron",count:1,components:{"minecraft:custom_data":{le_cauldron:1b,le_keep:1b},"minecraft:custom_name":{"text":"Котёл знахаря","italic":false,"color":"green"}}}}
playsound minecraft:block.metal.break block @a[distance=..16] ~ ~ ~ 1 0.9
kill @s
