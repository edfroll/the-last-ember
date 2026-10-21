# as a player with the carrier tag: only the player whose UUID is stored in storage last_ember:ember carrier stays the carrier.
# Guards against a second carrier (e.g. an offline player who kept the tag while the Ember was given to someone else).
execute unless data storage last_ember:ember carrier run data modify storage last_ember:ember carrier set from entity @s UUID
data modify storage last_ember:ember tmp set from storage last_ember:ember carrier
execute store success score #diff le.e run data modify storage last_ember:ember tmp set from entity @s UUID
execute if score #diff le.e matches 1 run tag @s remove le.carrier
