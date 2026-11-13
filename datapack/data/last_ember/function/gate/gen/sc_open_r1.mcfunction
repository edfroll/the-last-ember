# generated: the shortcut r1 is open from inside the region: both sides, forever
execute if score #sc_r1 le.gate matches 1 run return 0
scoreboard players set #sc_r1 le.gate 1
data modify storage last_ember:gates s.r1 set value {open:1b}
execute in minecraft:overworld positioned -380 111 -196 as @a[distance=..32] at @s run playsound minecraft:block.chain.break block @s -380 111 -196 1.5 0.7
execute in minecraft:overworld positioned -380 111 -196 run title @a[distance=..32] actionbar {"text": "Путь в Приют открыт.", "color": "gold"}
