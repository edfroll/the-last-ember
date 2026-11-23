# T-031: the hook of the quest «Внук звонаря»: the task of the Spider Thicket calls it when the hunter Toivo is saved (q 2)
# and writes the reward here (q 3). A stub until then: only the state.
execute if data storage last_ember:heather {q:1} run data modify storage last_ember:heather q set value 2
