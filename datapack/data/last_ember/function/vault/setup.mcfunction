# T-019: treasuries. Scores in le.vt (the layout: #m.<vault> main item, #m2 second, #o opened, #a golden apple, #e Mending, #b built, #st.<n> staff taken)
scoreboard objectives add le.vt dummy
function last_ember:vault/gen/const
execute unless score #ver le.vt = #genver le.vt run function last_ember:vault/relayout_auto
schedule function last_ember:vault/loop 20t replace
