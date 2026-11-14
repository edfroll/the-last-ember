# in the overworld: the poses of the Weepers and the core of the tree as the altar says (probes: weepers/gen/probe_*; after a restart,
# a rebuilt chunk or altar/reset the blocks come back by themselves)
execute store result score #wpc le.alt run function last_ember:weepers/gen/probe_core
execute if data storage last_ember:altars a.weepers{done:1b} if function last_ember:weepers/gen/probe_down run function last_ember:weepers/gen/statues_down
execute if data storage last_ember:altars a.weepers{done:1b} unless score #wpc le.alt matches 2 run function last_ember:weepers/gen/core_after
execute unless data storage last_ember:altars a.weepers{done:1b} if function last_ember:weepers/gen/probe_up run function last_ember:weepers/gen/statues_up
execute unless data storage last_ember:altars a.weepers{done:1b} unless score #wpc le.alt matches 1 run function last_ember:weepers/gen/core_before
