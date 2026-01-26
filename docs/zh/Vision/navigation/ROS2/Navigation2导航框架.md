# Navigation2导航框架

  - Navigation工程的核心：让机器人从A点安全地移动到B点（定位、全局路径规划、局部路径规划与避障、多点导航、插件式地图管理）

  - Nav2行为树运行框架

    - ```
      ros2 launch nav2_bringup tb3_simulation_launch.py
      ```

    - gazebo可能启动不了（sudo apt install ros-humble-turtlebot3*）（缺少TurtleBot3相关的功能包，需要退出conda环境）

    - Navigation2 Goal由GoalUpdater管理，当点击Navigation2 Goal时，onPoseSet()函数会被调用，并将其值(x,y,theta)传递给GoalUpdater对象

    - 整个nav2工程的行为管理都是由行为树管理

  <img src="./picture/tree.png" width=700 height=300>

  - 

    - 行为树节点对应的xml文件

    - 

    - ```xml
      <root main_tree_to_execute="MainTree">
        # 根节点
        <BehaviorTree ID="MainTree">
          # 次根节点：类型是RecoveryNode，名称：NavigateRecovery，左孩子：PipelineSequence，右孩子：ReactiveFallback
          <RecoveryNode number_of_retries="6" name="NavigateRecovery">
            # NavigateRecovery的左孩子  
            <PipelineSequence name="NavigateWithReplanning">
              <RateController hz="1.0">
                <RecoveryNode number_of_retries="1" name="ComputePathToPose">
                  # ComputePathToPose这个字段会被行为树解析，并构建对应的类实例.
                  <ComputePathToPose goal="{goal}" path="{path}" planner_id="GridBased"/>
                  <ClearEntireCostmap name="ClearGlobalCostmap-Context" service_name="global_costmap/clear_entirely_global_costmap"/>
                </RecoveryNode>
              </RateController>
              <RecoveryNode number_of_retries="1" name="FollowPath">
                <FollowPath path="{path}" controller_id="FollowPath"/>
                <ClearEntireCostmap name="ClearLocalCostmap-Context" service_name="local_costmap/clear_entirely_local_costmap"/>
              </RecoveryNode>
            </PipelineSequence>
            <ReactiveFallback name="RecoveryFallback">
              <GoalUpdated/>
              <SequenceStar name="RecoveryActions">
                <ClearEntireCostmap name="ClearLocalCostmap-Subtree" service_name="local_costmap/clear_entirely_local_costmap"/>
                <ClearEntireCostmap name="ClearGlobalCostmap-Subtree" service_name="global_costmap/clear_entirely_global_costmap"/>
                <Spin spin_dist="1.57"/>
                <Wait wait_duration="5"/>
              </SequenceStar>
            </ReactiveFallback>
          </RecoveryNode>
        </BehaviorTree>
      </root>
      ```

  <img src="./picture/nav2_goal.png">

  - 两大代价地图

    - 全局代价地图
    - 主要包含的图层有：
      - Static Map Layer：静态地图层，通常都是SLAM建立完成的静态地图
      - Obstacle Map Layer：障碍地图层，用于动态的记录传感器感知到的障碍物信息
      - Inflation Layer：膨胀层，在以上两层地图上进行膨胀
    - 局部代价地图
    - 通常包含的图层有：
      - Obstacle Map Layer：障碍地图层，用于动态的记录传感器感知到的障碍物信息
      - Inflation Layer：膨胀层，在障碍地图层上进行膨胀

  - 三个Action Server

    - 规划器可以被编写为具有以下功能的工具
      - 计算最短路径
      - 计算完整覆盖路径
      - 沿稀疏或预定义路线计算路径
    - 控制器可以被编写为具有以下功能的工具：
      - 跟随路径
      - 使用里程计坐标系中的检测器与充电站对接
      - 登上电梯
      - 与某个工具的接口

  - 状态估计（重要组件）

    - Nav2中，默认进行状态估计的组件是AMCL（自适应蒙特卡洛定位）
    - 在导航项目中，需要提供两个主要的坐标转换。map到odom的坐标变换由定位系统（定位，简图，SLAM）提供，odom到base_link的坐标转换由里程计系统提供
    - 在选择具体实现方式时遵循REP-105标准（至少必须为机器人构造一个包含map->odom->base_link->[sensorframes]的完整的TF树。TF2是ROS2中的时变坐标变换库，Nav2使用TF2来表达和获取时间同步的坐标变换。关于base_link的其余坐标转换应该是静态的）

  - 里程计可以来自许多数据源，包括激光雷达、车轮编码器、VIO和IMU。里程计的目标是提供基于机器人运动的平滑和炼血的局部坐标系。全局定位系统会相对全局坐标的坐标变换进行更新，以解决里程计的漂移问题

  - 代价地图过滤器

    - 使用代价地图过滤器可以实现以下功能：
    - 机器人永远不会进入禁区/安全区
    - 限速去，机器人进入这些区域的最大速度将受到限制
    - 机器人在工业环境和仓库中移动的首选通道

  - Nav2源码功能包拆解

    - ---

    - 控制器及其实现相关功能包

    - nav2_controller | 控制器

    - nav2_dwb_controller | DWB控制器，Nav2控制器的一个实现

    - nav2_regulated_pure_pursuit_controller | 纯追踪控制器，Nav2控制器的一个实现

    - ---

    - 规划器及其实现相关功能包

    - nav2_planner | Nav2规划器

    - nav2_navfn_planner　｜　navfn规划器，Nav2规划器的一个实现

    - smac_planner | smac规划器，Nav2规划器的一个实现

    - ---

    - 恢复器

    - nav2_recoveries | Nav2恢复器

    - ---

    - 行为树节点及其定义

    - nav2_bt_navigator |　导航行为树

    - nav2_behavior_tree | 行为树节点插件定义

    - ---

    - 地图和定位

    - nav2_map_server　｜　地图服务器

    - nav2_costmap_2d　｜　2D代价地图

    - nav2_voxel_grid | 体素栅格

    - nav2_amcl | 自适应蒙特卡洛定位。　　状态估计，输入地图、激光、里程计数据，输出机器人map和odom之间的位资关系。

    - ---

    - 通用插件系统管理等

    - nav2_bringup | 启动入口

    - nav2_common　｜　公共功能包

    - nav2_msgs　｜　通信相关消息定义

    - nav2_util | 常用工具

    - nav2_lifecycle_manager |节点生命周期管理器　

    - nav2_rviz_plugins | RVIZ插件

    - ---

    - 核心定义

    - nav2_core　｜　Nav2核心包

    - navigation2 | nav2导航汇总配置

    - ---

    - 应用

    - nav2_waypoint_follower | 路点跟踪

    - ---

    - 测试

    - nav2_system_tests | 系统测试

  - nav2_params.yaml参数修改

    - [【ROS2】【机器人导航navigation2】参数调整分析_ros中的参数修改-CSDN博客](https://blog.csdn.net/m0_63671696/article/details/130022551)
