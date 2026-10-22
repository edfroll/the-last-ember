# reward of consume_item (a grimoire was read to the end): a seer keeps the enchanted book; the others get the grimoire back
advancement revoke @s only last_ember:seer/grimoire
execute if entity @s[tag=le.class.seer] run return run function last_ember:seer/grimoire_ok
# the remainder is put into the inventory after the reward: the others are dealt with on the next tick (seer/grimoire_fix)
tag @s add le.grchk
