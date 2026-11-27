# T-034: every second: the difficulty (peaceful: the owners count as defeated), each lair loaded -> its second (the owner present, the
# empty lair, the decor, the window of the tower), the trophies of the absent players of a won fight when they are back
schedule function last_ember:treasury/second 20t replace
execute store result score #df le.tr run difficulty
function last_ember:treasury/gen/ogre/sec
function last_ember:treasury/gen/grotto/sec
function last_ember:treasury/gen/tower/sec
# a touch cooldown left by a fight that ended (its tick stopped): cleared
execute unless score #g.st le.tr matches 1 unless score #t.st le.tr matches 1 run tag @e[type=minecraft:player,tag=le.trcool] remove le.trcool
