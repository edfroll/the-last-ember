# T-028: the R1 fade (region/hook/fade_r1_lake): the lake turns to a swamp, the south colossus's raised arm lies in it, the sockets are
# empty, the colossi do not wake any more (castle/second shows it where the chunks are loaded)
scoreboard players set #faded le.cas 1
scoreboard players set #eyes le.cas 3
tag @a remove le.cwake
function last_ember:castle/save
