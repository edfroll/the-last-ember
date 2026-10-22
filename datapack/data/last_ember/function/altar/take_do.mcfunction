# macro pid aid key: an empty hand takes the key back (until the event)
execute if items entity @a[tag=le.clicker,limit=1] weapon.mainhand * run return run title @a[tag=le.clicker] actionbar {"text":"Освободи руку","color":"gray"}
$execute as @a[tag=le.clicker,limit=1] run function last_ember:altar/gen/hand_dispatch {id:"$(key)"}
$data modify storage last_ember:altars p.p$(pid).filled set value 0b
$data modify storage last_ember:keys k.$(key).st set value 0
$scoreboard players remove #fill_$(aid) le.alt 1
$kill @e[type=minecraft:item_display,tag=le.ped_item$(pid)]
$data modify entity @e[type=minecraft:text_display,tag=le.ped_lbl$(pid),limit=1,sort=nearest] text.color set value "dark_gray"
playsound minecraft:block.amethyst_block.break block @a[distance=..16] ~ ~ ~ 1 0.8
