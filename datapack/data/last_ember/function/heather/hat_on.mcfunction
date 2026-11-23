# T-031: as a zombie / zombie villager in the zone heather with nothing on the head: the hat (an invisible stick: a non-empty head slot
# keeps the sun off - Mob.burnUndead in 26.3 - and the stick is not damageable; fire from the players still burns), never dropped
item replace entity @s armor.head with minecraft:stick[minecraft:item_model="last_ember:heather_none",minecraft:custom_data={le_hat:1b}]
data modify entity @s drop_chances.head set value 0.0f
tag @s add le.hhat
