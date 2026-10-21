$execute store result score #n le.e if entity @e[type=#last_ember:monsters,distance=..$(r)]
$effect give @e[type=#last_ember:monsters,distance=..$(r)] minecraft:glowing 10 0 true
execute if score #n le.e matches 0 run title @s actionbar {"text":"Рог: врагов не видно","color":"gray"}
execute if score #n le.e matches 1.. run title @s actionbar {"text":"Рог: враги подсвечены","color":"gold"}
