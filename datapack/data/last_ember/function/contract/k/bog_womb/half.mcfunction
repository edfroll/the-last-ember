# at half health it bursts open and two small wombs crawl out (half the health and the blow of the big one each)
function last_ember:lab/s/womb_death2
particle minecraft:item_slime ~ ~1 ~ 1 0.5 1 0.1 40
$function last_ember:contract/k/bog_womb/small {id:"$(id)"}
$function last_ember:contract/k/bog_womb/small {id:"$(id)"}
tellraw @a[distance=..32] {"text":"Утроба лопается — из неё выползают ещё две!","color":"dark_green"}
