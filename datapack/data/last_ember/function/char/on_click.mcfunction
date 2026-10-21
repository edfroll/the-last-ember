# as the clicked interaction
data remove entity @s interaction
scoreboard players operation #id le.e = @s le.pid
execute as @a[tag=le.clicker,limit=1] run function last_ember:char/pad_click
