# macro s = stretch|squash|neutral|charge|splat|gone, d = ticks; the numbers for the big and the small one are in storage last_ember:lab womb
$execute if entity @s[tag=!le.lw_small] on passengers run data merge entity @s {start_interpolation:0,interpolation_duration:$(d),transformation:{translation:[0.0f,-1.513f,0.0f]}}
$execute if entity @s[tag=le.lw_small] on passengers run data merge entity @s {start_interpolation:0,interpolation_duration:$(d),transformation:{translation:[0.0f,-1.0f,0.0f]}}
$execute if entity @s[tag=!le.lw_small] on passengers run data modify entity @s transformation.scale set from storage last_ember:lab womb.big.$(s)
$execute if entity @s[tag=le.lw_small] on passengers run data modify entity @s transformation.scale set from storage last_ember:lab womb.small.$(s)
