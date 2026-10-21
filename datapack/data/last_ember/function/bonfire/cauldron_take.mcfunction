# as/at the cauldron interaction: only a sneaking healer takes it back; others just get a hint
execute unless entity @a[tag=le.clicker,tag=le.class.healer,predicate=last_ember:sneaking] run return run title @a[tag=le.clicker] actionbar {"text":"Котёл знахаря: снять его может только знахарь (Shift+ПКМ)","color":"gray"}
execute if block ~ ~ ~ minecraft:cauldron run setblock ~ ~ ~ minecraft:air
execute if block ~ ~ ~ minecraft:water_cauldron run setblock ~ ~ ~ minecraft:air
execute as @a[tag=le.clicker,limit=1] run give @s minecraft:cauldron[minecraft:custom_data={le_cauldron:1b,le_keep:1b},minecraft:custom_name={"text":"Котёл знахаря","italic":false,"color":"green"}] 1
playsound minecraft:block.metal.break block @a[distance=..16] ~ ~ ~ 1 0.9
kill @s
