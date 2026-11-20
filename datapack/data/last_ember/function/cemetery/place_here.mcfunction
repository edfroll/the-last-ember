# T-027: macro kind: the spirit stands here when here is the cemetery
execute unless predicate last_ember:cemetery/in_cem run return 0
$function last_ember:cemetery/spirit_$(kind)
scoreboard players set #ok le.cem 1
