def update_wall_visibility(props, is_algo_weaved) -> None:
    obj_walls = props.objects.walls
    obj_walls.hide_viewport = obj_walls.hide_render = props.wall_hide or (
        props.maze_weave > 0 and is_algo_weaved and not props.maze_weave_show_walls
    )
