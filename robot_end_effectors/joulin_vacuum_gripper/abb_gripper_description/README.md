


    cd ~/ws_moveit
    colcon build --packages-select abb_gripper_description abb_irb6700_with_rail_moveit_config
    source install/setup.bash
    ros2 launch abb_irb6700_with_rail_moveit_config demo.launch.py use_fake_hardware:=true