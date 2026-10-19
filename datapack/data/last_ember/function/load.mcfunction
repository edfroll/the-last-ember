# Runs on world load / reload.
scoreboard objectives add le.init dummy
scoreboard players set #loaded le.init 1
tellraw @a[tag=le.debug] {"text":"[Last Ember] datapack loaded","color":"gold"}
say [Last Ember] datapack loaded
