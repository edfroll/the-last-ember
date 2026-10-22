# as a player: gives the one valid Ember (current gen) and makes them the carrier. Test entry point: function last_ember:ember/give_to_me
function last_ember:ember/gen/give_dispatch
tag @s add le.carrier
data modify storage last_ember:ember carrier set from entity @s UUID
