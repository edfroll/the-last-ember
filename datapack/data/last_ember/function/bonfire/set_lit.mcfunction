# at the hearth (macro i r): lit campfire (signal smoke over hay), glowing nest, candles; registry state = 1
# T-023: lv = the look it shows (1 lit), faded = 0 (lit again after the fade of the region)
$function last_ember:bonfire/gen/lit_r$(r)
$data modify storage last_ember:bonfires by.b$(i) merge value {state:1,lv:1b,faded:0b}
