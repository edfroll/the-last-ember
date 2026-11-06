# generated: every 10 ticks, one call per key (uniqueness, loss, stale copies)
execute as @e[type=minecraft:item,tag=!le.kchk] if items entity @s contents minecraft:ominous_trial_key run tag @s add le.kitem
tag @e[type=minecraft:item,tag=!le.kchk] add le.kchk
scoreboard players add #kphase le.alt 1
execute if score #kphase le.alt matches 4.. run scoreboard players set #kphase le.alt 0
tag @a[tag=le.khas] remove le.khas
execute as @a[tag=!le.khas] if items entity @s container.* minecraft:ominous_trial_key run tag @s add le.khas
execute as @a[tag=!le.khas] if items entity @s weapon.offhand minecraft:ominous_trial_key run tag @s add le.khas
execute as @a[tag=!le.khas] if items entity @s player.cursor minecraft:ominous_trial_key run tag @s add le.khas
execute as @a[tag=!le.khas] if items entity @s armor.* minecraft:ominous_trial_key run tag @s add le.khas
execute as @a[tag=!le.khas] if items entity @s enderchest.* minecraft:ominous_trial_key run tag @s add le.khas
execute unless entity @a[tag=le.khas,limit=1] unless entity @e[type=minecraft:item,tag=le.kitem,limit=1] run return run function last_ember:altar/gen/keys_lost
function last_ember:altar/gen/kw_seal_magister with storage last_ember:keys k.seal_magister
function last_ember:altar/gen/kw_tear_creaker with storage last_ember:keys k.tear_creaker
function last_ember:altar/gen/kw_crown_witches with storage last_ember:keys k.crown_witches
function last_ember:altar/gen/kw_thread_labyrinth with storage last_ember:keys k.thread_labyrinth
function last_ember:altar/gen/kw_drop_source with storage last_ember:keys k.drop_source
function last_ember:altar/gen/kw_shell_sea_gods with storage last_ember:keys k.shell_sea_gods
function last_ember:altar/gen/kw_stone_black_water with storage last_ember:keys k.stone_black_water
function last_ember:altar/gen/kw_anchor_drowned with storage last_ember:keys k.anchor_drowned
function last_ember:altar/gen/kw_candle_unfading with storage last_ember:keys k.candle_unfading
function last_ember:altar/gen/kw_tear_titan with storage last_ember:keys k.tear_titan
function last_ember:altar/gen/kw_shard_ice_crown with storage last_ember:keys k.shard_ice_crown
function last_ember:altar/gen/kw_tablet with storage last_ember:keys k.tablet
function last_ember:altar/gen/kw_seal_whirl with storage last_ember:keys k.seal_whirl
function last_ember:altar/gen/kw_eye_forgotten_god with storage last_ember:keys k.eye_forgotten_god
function last_ember:altar/gen/kw_banner_dawn with storage last_ember:keys k.banner_dawn
function last_ember:altar/gen/kw_hammer_ancestors with storage last_ember:keys k.hammer_ancestors
function last_ember:altar/gen/kw_crown_mountain_king with storage last_ember:keys k.crown_mountain_king
function last_ember:altar/gen/kw_heart_silence with storage last_ember:keys k.heart_silence
