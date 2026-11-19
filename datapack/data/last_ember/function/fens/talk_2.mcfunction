# T-026: the Maiden, before the choice. The first talk: her introduction and (the first time anybody talks to her) 5 sedge bundles;
# later the bundles that were lost again (pools still open - bundles held by the players in the game); all 5 heads closed: the give button
execute unless entity @s[tag=le.fh2] run return run function last_ember:fens/intro_2
function last_ember:fens/sedge_again
function last_ember:fens/gen/count
execute if score #closed le.fn matches 5.. run scoreboard players enable @s le.fgive
execute if score #closed le.fn matches 5.. run return run dialog show @s last_ember:fens/give_2
dialog show @s last_ember:fens/wait_2
