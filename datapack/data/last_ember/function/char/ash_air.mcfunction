# as an ashborn with the eyes under water. Players' NBT cannot be written by commands (Air included), so "suffocation x3" is emulated:
# the air is read; when 100 ticks of the vanilla 300 are used (the vanilla air would have run out at x3 speed) the drowning damage starts
# (2 every 10 ticks, the shortest gap the invulnerability frames allow: twice the vanilla rate), and goes on until the air is back above 200
execute store result score #air le.e run data get entity @s Air
execute if score #air le.e matches ..200 run function last_ember:char/ash_hurt
