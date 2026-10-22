tellraw @s {"text":"Твоя сила растёт.","color":"gold"}
execute if entity @s[tag=le.class.knight] run tellraw @s {"text":"Щит держит крепче, клинок бьёт чаще.","color":"gray"}
execute if entity @s[tag=le.class.ranger] run tellraw @s {"text":"Стрелы летят точнее, рог слышен дальше.","color":"gray"}
execute if entity @s[tag=le.class.seer] run tellraw @s {"text":"Посохи гремят громче, Покров плотнее.","color":"gray"}
execute if entity @s[tag=le.class.healer] run tellraw @s {"text":"Зелья крепче, котёл щедрее.","color":"gray"}
playsound minecraft:entity.player.levelup player @s ~ ~ ~ 0.6 0.8
