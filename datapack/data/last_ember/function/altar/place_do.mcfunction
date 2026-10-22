# macro pid aid key gen: the clicker puts the key on its own pedestal
$execute unless items entity @a[tag=le.clicker,limit=1] weapon.mainhand *[minecraft:custom_data~{le_key:"$(key)",gen:$(gen)}] run return run function last_ember:altar/wrong_key
item replace entity @a[tag=le.clicker,limit=1] weapon.mainhand with minecraft:air
$data modify storage last_ember:altars p.p$(pid).filled set value 1b
$data modify storage last_ember:keys k.$(key).st set value 1
$data modify storage last_ember:keys k.$(key).got set value 1b
$scoreboard players add #fill_$(aid) le.alt 1
$summon minecraft:item_display ~ ~1.3 ~ {Tags:["le.ped_item","le.ped_item$(pid)"],billboard:"vertical",brightness:{sky:15,block:15},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.8f,0.8f,0.8f]},item:{id:"minecraft:ominous_trial_key",count:1,components:{"minecraft:item_model":"last_ember:key_$(key)"}}}
$data modify entity @e[type=minecraft:text_display,tag=le.ped_lbl$(pid),limit=1,sort=nearest] text.color set value "light_purple"
particle minecraft:enchant ~ ~1.2 ~ 0.3 0.3 0.3 0.5 20
playsound minecraft:block.amethyst_block.resonate block @a[distance=..16] ~ ~ ~ 1 1.2
function last_ember:altar/gen/check
