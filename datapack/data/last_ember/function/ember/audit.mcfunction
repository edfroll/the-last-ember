scoreboard players set #et le.e 0
function last_ember:ember/purge_stale with storage last_ember:ember
# a valid Ember on a non-carrier (should not happen): only one carrier may exist
execute as @a[tag=!le.carrier] if function last_ember:ember/has run function last_ember:ember/adopt
