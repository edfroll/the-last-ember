# generated: every 5 ticks: players in the transfer triggers of open shortcuts start the transfer
execute if score #sc_r1 le.gate matches 1 in minecraft:overworld positioned 28.8 103 -27.8 as @a[distance=..2.5,tag=!le.sct] unless score @s le.sccd > #gt le.gate run function last_ember:gate/gen/go_2
execute if score #sc_r1 le.gate matches 1 in minecraft:overworld as @a[x=-387,y=111,z=-198,dx=2,dy=2,dz=4,tag=!le.sct] unless score @s le.sccd > #gt le.gate run function last_ember:gate/gen/go_3
