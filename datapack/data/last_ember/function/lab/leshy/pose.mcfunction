# macro p = the pose (lab/gen/pose_<p>), d = ticks of the move
$data modify storage last_ember:lab anim.d set value $(d)
$function last_ember:lab/gen/pose_$(p) with storage last_ember:lab anim
