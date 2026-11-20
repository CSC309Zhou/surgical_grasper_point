# 与同一帧的分割消息对应，编号仅在该帧有效。
uint32 instance_id
# 原图坐标 xmin、ymin、xmax、ymax。
float32[4] bbox_xyxy
# 钳口点的原图像素坐标 x、y。
float32[2] point_xy
# 相对原始预测框的 u、v，允许超出 [0, 1]。
float32[2] point_box_uv
