# as a knight at a lit bonfire who has already been blessed today: a short hint after 5 s, then every 10 minutes
scoreboard players add @s le.bless 1
execute if score @s le.bless matches 5 run title @s actionbar {"text":"Благословение — завтра","color":"gray"}
execute if score @s le.bless matches 600.. run scoreboard players set @s le.bless 0
