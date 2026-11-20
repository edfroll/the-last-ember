# generated: every 5 ticks: a player whose 'chests opened' grew and who looks at a cursed chest within 6 blocks opens its curse
execute in minecraft:overworld positioned -478 135 367 as @a[distance=..7] if score @s le.chop > @s le.chopl run function last_ember:trap/ray_chest {n:1,i:"fens_ambush"}
