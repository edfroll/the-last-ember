# T-020: called from last_ember:load. Contracts on monsters: boards, the trail of clues, the monster of a contract, rituals, twins, choices (contract/gen/* from tools/gen_contracts.py)
scoreboard objectives add le.ct dummy
scoreboard objectives add le.cpn dummy
scoreboard objectives add le.chp dummy
scoreboard objectives add le.cdmg dummy
scoreboard objectives add le.cnum dummy
scoreboard objectives add le.cslot dummy
scoreboard objectives add le.cwk dummy
scoreboard objectives add le.ctake trigger
scoreboard objectives add le.choice trigger
scoreboard players set #64 le.ct 64
scoreboard players set #360 le.ct 360
scoreboard players set #10 le.ct 10
scoreboard players set #4 le.ct 4
scoreboard players set #3 le.ct 3
scoreboard players set #2 le.ct 2
execute unless score #pn_next le.ct matches 1.. run scoreboard players set #pn_next le.ct 1
function last_ember:contract/gen/init
schedule function last_ember:contract/loop 5t replace
