# T-031: every second of the freeze: still facing the belfry; after 10 s the awake and the vanilla ones go on, the resting ones rest
scoreboard players remove #frz le.hv 1
function last_ember:heather/gen/face_bell
execute if score #frz le.hv matches ..0 as @e[tag=le.hfrz] run function last_ember:heather/unfreeze
