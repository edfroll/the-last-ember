# every second: new players get the start bonfire; everyone's respawn point is re-applied
execute if score #start le.e matches 0.. as @a[scores={le.class=1..}] unless score @s le.sb matches -2147483648..2147483647 run function last_ember:bonfire/bind_start
execute as @a if score @s le.sb matches -2147483648..2147483647 run function last_ember:bonfire/apply_spawn
function last_ember:bonfire/gen/build_pending
schedule function last_ember:bonfire/spawn_loop 20t replace
