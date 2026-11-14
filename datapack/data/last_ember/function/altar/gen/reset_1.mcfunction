# generated: the altars of the chapter 1 back to the start (test): pedestals emptied, keys invalid and free, the event can run again;
# T-023: a chapter that was done is taken back (#chapters - 1, tiers, the lore of the Ember) and its hook altar/hook/reset_1 undoes the world
execute if data storage last_ember:altars a.weepers{done:1b} run scoreboard players remove #chapters le.alt 1
data modify storage last_ember:altars a.weepers.done set value 0b
data modify storage last_ember:altars a.weepers.ev set value -1
scoreboard players set #fill_weepers le.alt 0
data modify storage last_ember:altars p.p1.filled set value 0b
kill @e[type=minecraft:item_display,tag=le.ped_item1]
data modify entity @e[type=minecraft:text_display,tag=le.ped_lbl1,limit=1] text.color set value "dark_gray"
data modify storage last_ember:keys k.thread_labyrinth.st set value 0
data modify storage last_ember:keys k.thread_labyrinth.got set value 0b
data modify storage last_ember:keys k.thread_labyrinth.it set value 0b
data modify storage last_ember:keys k.thread_labyrinth.pend set value 0b
function last_ember:altar/gen_bump {key:"thread_labyrinth"}
data modify storage last_ember:altars p.p2.filled set value 0b
kill @e[type=minecraft:item_display,tag=le.ped_item2]
data modify entity @e[type=minecraft:text_display,tag=le.ped_lbl2,limit=1] text.color set value "dark_gray"
data modify storage last_ember:keys k.tear_creaker.st set value 0
data modify storage last_ember:keys k.tear_creaker.got set value 0b
data modify storage last_ember:keys k.tear_creaker.it set value 0b
data modify storage last_ember:keys k.tear_creaker.pend set value 0b
function last_ember:altar/gen_bump {key:"tear_creaker"}
data modify storage last_ember:altars p.p3.filled set value 0b
kill @e[type=minecraft:item_display,tag=le.ped_item3]
data modify entity @e[type=minecraft:text_display,tag=le.ped_lbl3,limit=1] text.color set value "dark_gray"
data modify storage last_ember:keys k.signet_king.st set value 0
data modify storage last_ember:keys k.signet_king.got set value 0b
data modify storage last_ember:keys k.signet_king.it set value 0b
data modify storage last_ember:keys k.signet_king.pend set value 0b
function last_ember:altar/gen_bump {key:"signet_king"}
data modify storage last_ember:altars p.p4.filled set value 0b
kill @e[type=minecraft:item_display,tag=le.ped_item4]
data modify entity @e[type=minecraft:text_display,tag=le.ped_lbl4,limit=1] text.color set value "dark_gray"
data modify storage last_ember:keys k.crown_witches.st set value 0
data modify storage last_ember:keys k.crown_witches.got set value 0b
data modify storage last_ember:keys k.crown_witches.it set value 0b
data modify storage last_ember:keys k.crown_witches.pend set value 0b
function last_ember:altar/gen_bump {key:"crown_witches"}
function last_ember:altar/chapters_changed
function last_ember:altar/hook/reset_1
