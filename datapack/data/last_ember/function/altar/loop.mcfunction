# every second: unbuilt altars, the check for the event, the tiers of the players, keys that are owed to players who came back
function last_ember:altar/gen/build_pending
function last_ember:altar/gen/check
function last_ember:altar/tier_sync
execute as @a run function last_ember:altar/gen/keys_join
schedule function last_ember:altar/loop 20t replace
