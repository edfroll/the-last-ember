# T-028: every second: the faded / living lake where loaded, the click box of the gate, the ambush getting ready again (10 minutes
# without players within 32 of the rest platform), the state in storage
function last_ember:castle/gen/fade_sync
function last_ember:castle/gen/gate_box
execute if score #amb le.cas matches 1 run function last_ember:castle/gen/ambush_near
execute if score #amb le.cas matches 1 if score #n32 le.cas matches 0 run scoreboard players add #ambt le.cas 1
execute if score #amb le.cas matches 1 if score #n32 le.cas matches 1.. run scoreboard players set #ambt le.cas 0
execute if score #amb le.cas matches 1 if score #ambt le.cas matches 600.. run scoreboard players set #amb le.cas 0
function last_ember:castle/save
