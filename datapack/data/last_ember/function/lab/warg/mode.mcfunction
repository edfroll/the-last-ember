# macro m = the mode, p = its first pose, d = ticks
$scoreboard players set @s le.lan $(m)
scoreboard players set @s le.lfd 0
scoreboard players set @s le.lfr 0
$function last_ember:lab/rig_pose {r:"warg",p:"$(p)",d:$(d)}
