# generated: the event of weepers ends: the chapter 1 is done
data modify storage last_ember:altars a.weepers.ev set value -1
data modify storage last_ember:altars a.weepers.done set value 1b
scoreboard players add #chapters le.alt 1
execute in minecraft:overworld as @a at @s if dimension minecraft:overworld run title @s title {"text":"Глава I завершена","color":"gold"}
execute in minecraft:overworld as @a at @s if dimension minecraft:overworld run title @s subtitle {"text":"Уголь получил свойство: Свет","color":"yellow"}
execute in minecraft:overworld as @a at @s if dimension minecraft:overworld run playsound minecraft:ui.toast.challenge_complete player @s ~ ~ ~ 1 1
function last_ember:altar/key_done {key:"thread_labyrinth"}
function last_ember:altar/key_done {key:"tear_creaker"}
function last_ember:altar/key_done {key:"signet_king"}
function last_ember:altar/key_done {key:"crown_witches"}
function last_ember:altar/chapters_changed
function last_ember:altar/hook/chapter_1
