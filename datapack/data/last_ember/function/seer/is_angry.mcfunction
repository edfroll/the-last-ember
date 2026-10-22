# as a neutral mob: 1 = it is angry now (anger_end_time in the future, or a piglin with an angry_at memory) and is not tamed; 0 = calm or tamed (we do not touch them)
# piglins and brutes are hostile in our Nether by design: always targets
execute if entity @s[type=#last_ember:always_target] run return 1
execute if data entity @s Owner run return 0
execute if data entity @s owner run return 0
scoreboard players set #ae le.e 0
execute store result score #ae le.e run data get entity @s anger_end_time
execute if score #ae le.e > #gt le.e run return 1
execute if data entity @s Brain.memories."minecraft:angry_at" run return 1
return 0
