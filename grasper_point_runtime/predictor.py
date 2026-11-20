import numpy as np
import torch

from .geometry import INPUT_SIZE, box_coordinates, crop_mask, valid_heatmap


class PointPredictor:
    def __init__(self, artifact, device):
        self.device = torch.device(device)
        self.model = torch.export.load(artifact).module().to(self.device)

    @torch.inference_mode()
    def predict(self, mask, box):
        canvas, scale, offset = crop_mask(mask, box)
        if not canvas[0].any():
            return None
        tensor = torch.from_numpy(canvas[None, :1]).to(self.device, dtype=torch.float32)
        valid = torch.from_numpy(valid_heatmap(canvas)[None]).to(self.device)
        point = self.model(tensor, valid)[0].cpu().numpy()
        canvas_xy = (point + 1) * (INPUT_SIZE / 2) - 0.5
        image_xy = (canvas_xy - offset) / scale
        if not np.isfinite(image_xy).all():
            raise FloatingPointError("Point 模型输出了非有限坐标")
        return image_xy.tolist(), box_coordinates(image_xy, box).tolist()
