# T-027: as the Magister every 10 ticks: a sword when a player is within 7, a bow when nobody is
execute if entity @a[gamemode=!spectator,distance=..7] unless items entity @s weapon.mainhand minecraft:iron_sword run item replace entity @s weapon.mainhand with minecraft:iron_sword
execute unless entity @a[gamemode=!spectator,distance=..7] unless items entity @s weapon.mainhand minecraft:bow run item replace entity @s weapon.mainhand with minecraft:bow
particle minecraft:soul ~ ~1.2 ~ 0.3 0.6 0.3 0.01 2 normal
