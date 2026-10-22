# reward of consume_item: a staff held for the full 10 s (the full charge of the Wrath)
advancement revoke @s only last_ember:seer/consume
execute unless entity @s[tag=le.class.seer] run return 0
execute if score @s le.wchg matches 0.. run function last_ember:seer/wrath_release
scoreboard players set @s le.suse 0
