import torch
import torchvision
from torchvision.models.detection import maskrcnn_resnet50_fpn
from PIL import Image
import cv2
import numpy as np
import os


class MaskRCNNDetector:
    """Mask R-CNN を使用した犬猫検出"""
    
    # COCO クラスのカテゴリID
    COCO_INSTANCE_CATEGORY_NAMES = [
        '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
        'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
        'parking meter', 'bench', 'cat', 'dog', 'horse', 'sheep', 'cow',  # cat=16, dog=17
        'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
        'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
        'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle',
        'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
        'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table', 'N/A', 'N/A',
        'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'microwave', 'oven',
        'toaster', 'sink', 'refrigerator', 'N/A', 'book', 'clock', 'vase', 'scissors',
        'teddy bear', 'hair drier', 'toothbrush'
    ]
    
    CAT_ID = 16
    DOG_ID = 17
    
    def __init__(self, device='cpu', confidence_threshold=0.5):
        """
        Args:
            device (str): 'cpu' or 'cuda'
            confidence_threshold (float): 検出の信頼度閾値
        """
        self.device = device
        self.confidence_threshold = confidence_threshold
        
        # Mask R-CNN (COCO学習済み) をロード
        self.model = maskrcnn_resnet50_fpn(pretrained=True)
        self.model.to(device)
        self.model.eval()
    
    def detect(self, image_path):
        """
        画像から犬・猫を検出
        
        Args:
            image_path (str): 画像ファイルパス
            
        Returns:
            dict: {
                'dog_count': int,
                'cat_count': int,
                'total_count': int,
                'label': str ('dog', 'cat', 'both', 'other'),
                'confidence': float,
                'detections': list of dicts
            }
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # 画像の読み込み
        image = Image.open(image_path).convert('RGB')
        image_array = np.array(image)
        
        # PyTorch テンソルに変換
        image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).float()
        image_tensor = image_tensor / 255.0  # 正規化
        image_tensor = image_tensor.to(self.device)
        
        # 推論
        with torch.no_grad():
            predictions = self.model([image_tensor])
        
        pred = predictions[0]
        
        # 犬と猫のみを抽出
        dog_count = 0
        cat_count = 0
        detections = []
        
        boxes = pred['boxes']
        labels = pred['labels']
        scores = pred['scores']
        masks = pred['masks']
        
        for i, (box, label, score, mask) in enumerate(zip(boxes, labels, scores, masks)):
            if score.item() < self.confidence_threshold:
                continue
            
            if label.item() == self.DOG_ID:
                dog_count += 1
                detection_type = 'dog'
            elif label.item() == self.CAT_ID:
                cat_count += 1
                detection_type = 'cat'
            else:
                continue
            
            detections.append({
                'type': detection_type,
                'box': box.cpu().numpy(),
                'score': score.item(),
                'mask': mask[0].cpu().numpy()
            })
        
        # ラベルを決定
        total_count = dog_count + cat_count
        if dog_count > 0 and cat_count > 0:
            label = 'both'
            confidence = (dog_count + cat_count) / 2 * 100  # 平均信頼度
        elif dog_count > 0:
            label = 'dog'
            confidence = 90 + (dog_count * 5)  # 犬が多いほど信頼度UP
        elif cat_count > 0:
            label = 'cat'
            confidence = 90 + (cat_count * 5)  # 猫が多いほど信頼度UP
        else:
            label = 'other'
            confidence = 0.0
        
        # 信頼度は0～100の範囲に収める
        confidence = min(confidence / 100, 1.0)
        
        return {
            'dog_count': dog_count,
            'cat_count': cat_count,
            'total_count': total_count,
            'label': label,
            'confidence': confidence,
            'detections': detections
        }
    
    def draw_boxes(self, image_path, output_path, detections):
        """
        検出結果をボックスで画像に描画
        
        Args:
            image_path (str): 入力画像パス
            output_path (str): 出力画像パス
            detections (list): 検出結果のリスト
        """
        image = cv2.imread(image_path)
        
        # 色定義
        dog_color = (0, 255, 0)  # 緑：犬
        cat_color = (255, 0, 0)  # 青：猫
        
        for detection in detections:
            box = detection['box']
            score = detection['score']
            det_type = detection['type']
            
            # ボックスの座標
            x1, y1, x2, y2 = map(int, box)
            
            # 色を選択
            color = dog_color if det_type == 'dog' else cat_color
            
            # ボックスを描画
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # ラベルテキスト
            label_text = f"{det_type}: {score:.2f}"
            cv2.putText(image, label_text, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # 出力
        cv2.imwrite(output_path, image)
        return output_path


# グローバルインスタンス
detector = None


def init_detector(device='cpu'):
    """検出器の初期化"""
    global detector
    detector = MaskRCNNDetector(device=device)


def get_detector():
    """検出器のインスタンスを取得"""
    global detector
    if detector is None:
        init_detector()
    return detector
