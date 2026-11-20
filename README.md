# surgical_grasper_point

独立的 ROS 2 Humble 节点。订阅 `surgical_perception` 发布的抓钳实例，使用 CNN 热图和 DSNT 定位钳口点。每把抓钳发布一个点，`grasper1` 和 `grasper2` 共用同一个预测模型。输出实例编号只在当前帧有效。

## 构建和启动

在 Ubuntu 22.04 和 ROS 2 Humble 上，先构建并加载上游 [surgical_perception_lab](https://github.com/CSC309Zhou/surgical_perception_lab)。使用它已经启用的 Python 3.10 虚拟环境，导出模型使用 PyTorch 2.14.1，显卡联调使用对应的 CUDA 12.6 版本。依赖还包括上游环境中的 NumPy、OpenCV 和 ROS `cv_bridge`。

在已加载上游工作空间的终端中，把本仓库放入新工作空间的 `src` 目录，然后在该工作空间根目录运行以下命令。

```bash
colcon build --packages-select surgical_grasper_point \
  --cmake-args -DPython3_EXECUTABLE="$(command -v python3)"
source install/setup.bash
ros2 launch surgical_grasper_point point.launch.py device:=cuda:0
```

默认设备为 `cpu`，输入话题可以通过 `input_topic` 修改。复现实验时，上游分割使用 s 型微调权重，`imgsz=640`，置信度阈值为 `0.25`。

## 话题

| 方向 | 默认话题 | 消息类型 |
| --- | --- | --- |
| 输入 | `/surgical_perception/instances` | `surgical_perception/msg/InstrumentArray` |
| 输出 | `/surgical_grasper_point/points` | `surgical_grasper_point/msg/GrasperPointArray` |

两个话题均使用 BEST_EFFORT、KEEP_LAST，队列深度为 1。输出保留原图时间戳、`frame_id`、图像尺寸、原预测框和帧内 `instance_id`。每个点同时提供原图像素坐标 `point_xy` 和相对原预测框的坐标 `point_box_uv`。点超出原预测框时，相对坐标可以超出 `[0, 1]`。输入中没有有效抓钳时，节点发布空数组。

```bash
ros2 topic echo /surgical_grasper_point/points --qos-reliability best_effort
```

## 模型

`weights/point_head.pt2` 来自热图模型第 66 轮的最佳权重。输入是扩框后等比例缩放得到的 `192×192` 单实例掩膜，模型在整个有效裁剪区域定位，因此点可以落在张开钳口之间的空隙。

## Ubuntu 联调

- RTX 4060 上回放 42 张测试原图，核对了 57 个参考点，其中 15 张为双抓钳同框。ROS 输出的点与离线推理坐标最大相差 0.017 个原图像素。
- 用内置摄像头通过 `endoscope_device` 采集。8 秒内有 239 帧在采集、分割和 Point 三个话题上保留相同时间戳。这次摄像头画面无抓钳，Point 话题发布空数组。
