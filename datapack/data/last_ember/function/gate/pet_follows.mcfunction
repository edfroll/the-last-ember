# as a tame animal near the player le.scme: his own and not sitting (read once, at the moment of the transfer)
execute if entity @s[nbt={Sitting:1b}] run return 0
return run execute on owner if entity @s[tag=le.scme]
