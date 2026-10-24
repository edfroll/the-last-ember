# FOR EDWARD (as a player): five lab samples in a row 12 blocks ahead, 16 blocks apart, each on its own little patch, hidden until you come within 9 blocks.
# Survival or adventure mode (in creative they do not wake). Remove all: function last_ember:lab/clear
function last_ember:lab/clear
execute at @s rotated ~ 0 positioned ^32 ^ ^14 align xyz positioned ~0.5 ~ ~0.5 run function last_ember:lab/st_drowner
execute at @s rotated ~ 0 positioned ^16 ^ ^14 align xyz positioned ~0.5 ~ ~0.5 run function last_ember:lab/st_warg
execute at @s rotated ~ 0 positioned ^ ^ ^14 align xyz positioned ~0.5 ~ ~0.5 run function last_ember:lab/st_womb
execute at @s rotated ~ 0 positioned ^-16 ^ ^14 align xyz positioned ~0.5 ~ ~0.5 run function last_ember:lab/st_leshy
execute at @s rotated ~ 0 positioned ^-32 ^ ^14 align xyz positioned ~0.5 ~ ~0.5 run function last_ember:lab/st_fish
tellraw @s {"text":"Пять образцов стоят в ряд впереди, слева направо 1–5. Подойди к каждому ближе 9 блоков — проснётся. Убрать: /function last_ember:lab/clear","color":"gray"}
