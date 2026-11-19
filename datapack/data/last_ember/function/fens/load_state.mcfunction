# T-026: the state scores from the storage (a new world: the defaults); a reload keeps the scores, a lost scoreboard comes back from the storage
execute unless data storage last_ember:fens vial run data modify storage last_ember:fens vial set value {key:"fens_vial",gen:1}
execute unless data storage last_ember:fens skull run data modify storage last_ember:fens skull set value {key:"fens_skull",gen:1}
execute unless data storage last_ember:fens s run data modify storage last_ember:fens s set value {vs:0,sg:0,ms:0,sk:0,mt:0}
execute unless data storage last_ember:fens pools run data modify storage last_ember:fens pools set value {}
execute unless score #choice le.fn = #choice le.fn store result score #choice le.fn run data get storage last_ember:choices fens
execute unless score #vs le.fn = #vs le.fn store result score #vs le.fn run data get storage last_ember:fens s.vs
execute unless score #sg le.fn = #sg le.fn store result score #sg le.fn run data get storage last_ember:fens s.sg
execute unless score #ms le.fn = #ms le.fn store result score #ms le.fn run data get storage last_ember:fens s.ms
execute unless score #mt le.fn = #mt le.fn store result score #mt le.fn run data get storage last_ember:fens s.mt
execute unless score #sk le.fn = #sk le.fn store result score #sk le.fn run data get storage last_ember:fens s.sk
execute unless score #p1 le.fn = #p1 le.fn run function last_ember:fens/gen/pools_load
# a risen Master that was not saved as such (the server stopped): he is in the world still (persistent) or not; the tick sorts it out
function last_ember:fens/gen/count
