# the Wrath of the Dead Sky: the first tick of holding the button: if the cooldown is over, the charge starts (the sky darkens for everybody until the last charger lets go)
execute if score #gt le.e < @s le.cd7 run return run function last_ember:seer/cd_msg {n:7}
scoreboard players set @s le.wchg 0
execute unless score #wact le.e matches 1 run function last_ember:seer/weather_save
playsound minecraft:block.beacon.activate player @a[distance=..24] ~ ~ ~ 1 0.6
