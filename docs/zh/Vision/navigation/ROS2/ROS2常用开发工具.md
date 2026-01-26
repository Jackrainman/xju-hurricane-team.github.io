  ## ROS2常用开发工具

  ​	在机器人的开发过程中，坐标变换非常重要且不好处理，ROS 2 就基于话题通信设计了一套库和工具，用于管理机器人坐标变换

  ​	1.**坐标变换工具介绍（TF)**

  ​	(1)**通过命令行使用TF**

  ​	ros2 run tf2_ros static_transform_publisher --x 0.1 --y 0.0 --z 0.2 --roll 0.0--pitch 0.0 --yaw 0.0 --frame-id base_link --child-frame-id base_laser

  ​	参数 --x 0.1 --y 0.0 --z 0.2 指定 base_link 到 base_laser 的平移量，其中 x、y、z 分别代表子坐标系在父坐标系下的 x、y、z 坐标轴上的平移距离，单位为 m。而 参 数 --roll 0.0 --pitch 0.0 --yaw 0.0 指 定 子 坐 标 系 相 对 于 父 坐 标 系 的 旋 转 量，roll、pitch、yaw 分别代表绕子坐标系的 x、y、z 轴旋转的欧拉角，单位为 rad。最后两个参数分别用于指定父坐标系和子坐标系的名称。

  ​	除了四元数和欧拉角，还有其他用于表示姿态的方式，通过 ROS 2 中的 mrpt2 工具，可以方便地获取不同姿态表示之间的对应关系和可视化

  - 四元数是一种用于标识三维空间中姿态的数学工具，在ROS2中经常被用于机器人的姿态描述等方面

  四元数由一个实部和三个虚部组成，通常表示为q = w + xi +yj + zk

  ​	sudo apt install ros-humble-mrpt-*（这个是下载工具）

  ​	3d-rotation-converter（打开工具）

  ​	ros2 run tf2_ros static_transform_publisher --x 0.3 --y 0.0 --z 0.0 --roll 0.0 --pitch 0.0 --yaw 0.0 --frame-id base_laser --child-frame-id wall_point

  ​	`rotation: ('0.000000', '0.000000', '0.000000', '1.000000')`：

  ​	最后一个1.000000是四元数的实部

  ​	在真实的机器人中，固定不变的坐标关系才会使用静态坐标变换，而对于障碍物信息应该使用动态的坐标变换，前面三个是虚部。但是改变实部会改变四元素所代表的旋转状态，就是实部与旋转角度有关，虚部与旋转轴有关

  ​	--frame-id是用于指定坐标变换的父坐标系名称的参数

  ​	ros2 run tf2_ros tf2_echo base_link wall_point

  ​	tf2_echo 用于输入两个坐标之间的平移和旋转关系，第一个参数是父坐标系名称，第二个参数是子坐标系名称。

  ​	除了可以通过命令行计算坐标之间的关系外，还可以使用工具查看所有坐标系之间的连接关系

  ​	ros2 run tf2_tools view_frames（需要将坐标转换的代码一直开着才能看到）

  ​	该命令会将当前所有广播的坐标关系通过图形的方式表示出来，并在当前目录生成一个PDF 文件和 GV 格式文件

  - 注意：统一参考系，统一以机器人的基坐标系为标准

  ​	（2）**对TF原理的简单探究**

  ​	ros2 topic list

  ​	当发布静态广播时，广播的数据就会通过话题通信发布到 /tf_static 话题上

  ​	ros2 topic info /tf_static

  ​	输入命令查看话题的具体信息

  ​	ros2 interface show tf2_msgs/msg/TFMessage

  ​	查看改话题的消息接口类型是tf2_msgs/msg/TFMesage

  ​	需要注意当发布动态 TF 时，数据将发布到名称为 /tf 的话题上。当需要查询坐标变换关系时，则会订阅 /tf 和 /tf_static 话题，通过数据中坐标之间的关系计算要查询的坐标之间的关系，这就是 TF 的工作原理

  ​	（3）**C++中的地图坐标系变换**

  - 通过C++发布静态TF

  ​	ros2 pkg create demo_cpp_tf --build-type ament_cmake --dependencies rclcpp tf2tf2_ros geometry_msgs tf2_geometry_msgs --license Apache-2.0	

  ​	ros2 run tf2_ros tf2_echo map target_point

  ​	来查看坐标关系

  - 通过C++发布动态TF

    发布动态 TF 和发布静态 TF 相比，最大的不同在于动态 TF 需要不断向外发布

  - 通过C++查询TF关系

    需要三个节点都开启才有结果

  ​	2.**常用可视化工具rqt与RViz**

  ​	（1）**GUI框架rqt**

  ​	我们在前面章节中使用过 rqt，比如使用它查看节点关系、请求服务等。在任意终端输入rqt 命令就可以启动 rqt

  ​	rqt 是一个 GUI 框架，可以将各种插件工具加载为可停靠的窗口。目前没有选择插件，要添加插件，请从 Plugins菜单中选择项目

  ​	掌握如何安装新的 rqt 插件（其实就是下载完以后，在Plugins里面点击使用就行），以安装tf查看工具rqt-tf-tree为例

  ​	sudo apt install ros-humble-rqt-tf-tree -y

  ​	该工具将安装到 ROS 2 的默认安装目录下，安装完成后需要删除 rqt 的默认配置文件，才能让 rqt 重新扫描和加载到这个工具

  ​	rm -rf ～/.config/ros.org/rqt_gui.ini

  ​	执行所有操作后，可能没有任何响应（需要重启电脑，然后重新执行一次）

  ​	重新启动 rqt，然后选择 Plugins → Visualization → TF Tree 选项，即可打开 TF Tree 插件，运行 5.3 节的 TF 发布节点，单击左上角的 Refresh 按钮

  ​	sudo apt install ros-$ROS_DISTRO-rqt-＊

  ​	安装rqt所有相关组件

  ​	（2）**数据可视化工具RViz**

  ​	在学习 TF 时，虽然可以通过 tf2_tools 或 rqt-tf-tree 查看 TF 数据帧之间的关系，但并不能直观地看到它们在空间中的关系，而 RViz 不仅可以帮助我们实现坐标变换可视化，还可以实现机器人的传感器数据、3D 模型、点云、激光雷达数据等数据的可视化与交互。	

  ​	在任意终端输入 rviz2 即可打开 RViz

  ​	RViz 窗口左侧的 Displays 部分用于控制显示的数据。当需要显示某个数据时，可以单击Displays 窗口下方的 Add 按钮添加要显示的视图

  ​	在 By display type 选项卡中选择 TF，然后单击右下方的 OK 按钮。接着观察图 5-8 中间的网格，即可看到 TF 的显示结果，此时可以使用鼠标拖动显示视图，调整观察角度

  ​	选中 TF 视图选项下的 Show Names，在坐标系中添加对应的坐标系名称，接着修改Marker Scale 选项为 6，放大坐标轴和名字

  ​	如果想从机器人的视角 base_link 来观察目标点 target_point，只需要将机器人固定在原点即可，Displays 窗口中全局选项 Global Options 下的 Fixed Frame 就是用于显示右侧视图原点的坐标系名称的，我们修改为 base_link

  ​	默认的宽度为 1m，修改 Grid 下 Cell Size 的值，就可以修改网格宽度

  ​	RViz 还支持将当前的配置保存到文件中，方便下次直接加载使用，单击标题栏的 File → Save Config As 或者直接按 Ctrl+Shift+S 键即可弹出如图 5-13 所示的保存窗口

  ​	rviz2 -d ～/chapt5/rviz_tf.rviz

  ​	启动RViz并指定配置文件

  ​	（3）**数据记录工具ros2 bag**

  ​	首先在新的终端运行海龟模拟器，接着再打开新的终端，启动海龟键盘控制节点

  ​	ros2 bag record /turtle1/cmd_vel

  ​	如果直接使用 ros2 bagrecord 将录制所有的话题数据，不过我并不推荐这样做，有些数据并不是必需的，我们只需要将自己关心的话题名称依次放到命令后，进行录制即可

  ​	接着在键盘控制节点窗口使用方向箭头移动海龟，然后在话题录制终端按 Ctrl+C 键打断录制，ros2 bag record 在收到打断指令后就会停止录制并将数据保存到文件中

  ​	在终端 bags 目录下使用 ls 命令，可以看到录制数据存放的目录名

  ​	这个文件夹是按照时间命名的，文件夹中存放了两个文件，其中以 .db3 结尾的是存储话题数据的数据库文件，metadata.yaml 是记录的描述文件，使用 cat 查看该文件内容的命令

  ​	该文件中描述了被记录的话题名称和类型等信息，还保存了开始记录时间、持续时间、消息的数量等信息	

  ​	关闭键盘控制节点，然后重启海龟模拟器，现在来重新播放海龟的控制命令，对话题数据进行重播

  ​	ros2 bag play rosbag2_2023_12_11-01_57_18/（给我用绝对路径）

  ​	bag play 加文件夹名称，用于播放对应文件夹里的话题数据。运行完命令观察海龟窗口，海龟按照刚刚的控制轨迹移动

  ​	在重新播放话题时还有很多其他操作，例如按空格键可以暂停和继续播放，按上下键可以加快和减慢播放速度，按右键可以播放下一个消息。可以使用--help来查看
