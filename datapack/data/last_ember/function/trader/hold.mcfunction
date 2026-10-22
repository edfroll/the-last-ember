# macro x y z yaw, as a trader at its place: it cannot be taken away (pushed, boated, put in a minecart)
execute on vehicle run ride @s dismount
$execute unless entity @s[distance=..0.3] run tp @s $(x) $(y) $(z) $(yaw) 0
ride @s dismount
