# every tick, as a seer who has been using a staff: no use tick for 2 ticks = the button was released
scoreboard players operation #d le.e = #gt le.e
scoreboard players operation #d le.e -= @s le.slast
execute if score #d le.e matches ..1 run return 0
function last_ember:seer/released
scoreboard players set @s le.suse 0
