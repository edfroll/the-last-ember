# the green stinking trail: a low cloud that stays 6 s; who walks through it feels sick (hunger 3 s)
summon minecraft:area_effect_cloud ~ ~0.05 ~ {Tags:["le.lab_trail"],Radius:0.9f,RadiusPerTick:-0.004f,RadiusOnUse:0.0f,Duration:120,WaitTime:0,ReapplicationDelay:30,custom_particle:{type:"minecraft:dust",color:[0.33,0.52,0.08],scale:1.3},potion_contents:{custom_color:5470743,custom_effects:[{id:"minecraft:hunger",amplifier:1,duration:60,show_particles:0b}]}}
particle minecraft:falling_spore_blossom ~ ~0.6 ~ 0.4 0.2 0.4 0 2
