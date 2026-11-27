# T-034: the owners of the treasuries of R1 (the Ogre's Den, the Grotto of the Jelly, the Locked Tower), called from last_ember:load.
# Blocks: tools/build/r1_ogre.py, r1_grotto.py, castle_tower.py (offline); the generated part: function/treasury/gen/<ogre|grotto|tower>/*
# and advancement/treasury/* (tools/build/treasury_dp.py, the scores explained there). The chests are vaults of T-019 (r1_ogre, r1_grotto,
# r1_tower, build=0), locked by a block over them while the owner lives.
scoreboard objectives add le.tr dummy
scoreboard objectives add le.trg dummy
scoreboard objectives add le.trt dummy
scoreboard objectives add le.trs dummy
scoreboard objectives add le.tri dummy
scoreboard objectives add le.trv dummy
scoreboard objectives add le.trw dummy
scoreboard objectives add le.trp dummy
scoreboard objectives add le.trd dummy
scoreboard objectives add le.trb dummy
scoreboard objectives add le.trcd dummy
scoreboard objectives add le.trh dummy
scoreboard objectives add le.trf_o dummy
scoreboard objectives add le.trf_g dummy
scoreboard objectives add le.trf_t dummy
execute unless data storage last_ember:treasury ogre.state run data modify storage last_ember:treasury ogre.state set value 0
execute unless data storage last_ember:treasury grotto.state run data modify storage last_ember:treasury grotto.state set value 0
execute unless data storage last_ember:treasury tower.state run data modify storage last_ember:treasury tower.state set value 0
execute store result score #o.st le.tr run data get storage last_ember:treasury ogre.state
execute store result score #g.st le.tr run data get storage last_ember:treasury grotto.state
execute store result score #t.st le.tr run data get storage last_ember:treasury tower.state
# a restart (or a reload) during a fight: asleep again, a new generation (what the fight left vanishes when its chunks load)
execute if score #o.st le.tr matches 1 run scoreboard players add #o.g le.tr 1
execute if score #o.st le.tr matches 1 run scoreboard players set #o.st le.tr 0
execute if score #g.st le.tr matches 1 run scoreboard players add #g.g le.tr 1
execute if score #g.st le.tr matches 1 run scoreboard players set #g.st le.tr 0
execute if score #t.st le.tr matches 1 run scoreboard players add #t.g le.tr 1
execute if score #t.st le.tr matches 1 run scoreboard players set #t.st le.tr 0
scoreboard players add #o.g le.tr 0
scoreboard players add #g.g le.tr 0
scoreboard players add #t.g le.tr 0
scoreboard players set #o.die le.tr -1
scoreboard players set #g.die le.tr -1
scoreboard players set #t.die le.tr -1
scoreboard players set #t.gone le.tr -1
scoreboard players set #o.sw le.tr -1
scoreboard players add #o.won le.tr 0
scoreboard players add #g.won le.tr 0
scoreboard players add #t.won le.tr 0
execute store result storage last_ember:treasury ogre.state int 1 run scoreboard players get #o.st le.tr
execute store result storage last_ember:treasury grotto.state int 1 run scoreboard players get #g.st le.tr
execute store result storage last_ember:treasury tower.state int 1 run scoreboard players get #t.st le.tr
scoreboard players set #-1 le.tr -1
scoreboard players set #2 le.tr 2
scoreboard players set #4 le.tr 4
scoreboard players set #6 le.tr 6
scoreboard players set #8 le.tr 8
scoreboard players set #10 le.tr 10
scoreboard players set #20 le.tr 20
scoreboard players set #25 le.tr 25
scoreboard players set #40 le.tr 40
scoreboard players set #90 le.tr 90
scoreboard players set #100 le.tr 100
scoreboard players set #24000 le.tr 24000
schedule function last_ember:treasury/loop 5t replace
schedule function last_ember:treasury/second 20t replace
