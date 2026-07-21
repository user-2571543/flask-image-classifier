import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os


class ImageClassifier:
    """犬猫分類専用モデル（ResNet50 + 改善版）"""
    
    def __init__(self, device='cpu'):
        """
        Args:
            device (str): 'cpu' or 'cuda'
        """
        self.device = device
        
        # ResNet50の読み込み（ImageNet学習済みモデル）
        # より深いモデルで精度向上
        self.model = models.resnet50(pretrained=True)
        self.model.to(device)
        self.model.eval()
        
        # 入力変換パイプライン（標準化を改善）
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        
        # ImageNet クラスのマッピング
        self.class_mapping = self._create_class_mapping()
    
    def _create_class_mapping(self):
        """ImageNetクラスIDを dog/cat/other に変換するマッピング"""
        # ImageNetの犬クラス: 151-268
        dog_classes = set(range(151, 269))  # Chihuahua から Corgi まで
        
        # ImageNetの猫クラス: 281-285
        cat_classes = {281, 282, 283, 284, 285}  # Tabby, Tiger cat, Persian, Siamese, Egyptian cat
        
        mapping = {}
        for class_id in dog_classes:
            mapping[class_id] = 'dog'
        for class_id in cat_classes:
            mapping[class_id] = 'cat'
        
        return mapping
    
    def predict(self, image_path):
        """
        画像を分類して結果を返す
        
        Args:
            image_path (str): 画像ファイルパス
            
        Returns:
            tuple: (label, confidence)
                label (str): 'dog', 'cat', or 'other'
                confidence (float): 信頼度 (0.0 ~ 1.0)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # 画像の読み込み
        image = Image.open(image_path).convert('RGB')
        
        # 前処理と推論
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            top_prob, top_idx = torch.max(probabilities, dim=1)
        
        class_id = top_idx.item()
        confidence = top_prob.item()
        
        # ImageNetクラスをdog/cat/otherに変換
        label = self.class_mapping.get(class_id, 'other')
        
        # 信頼度が低い場合は 'other' に変更
        if confidence < 0.3:
            label = 'other'
        
        return label, confidence
    
    def predict_with_top_k(self, image_path, k=3):
        """
        Top-K予測結果を返す（デバッグ用）
        
        Args:
            image_path (str): 画像ファイルパス
            k (int): 上位K件を返す
            
        Returns:
            list: [(label, confidence), ...] のリスト
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            top_probs, top_indices = torch.topk(probabilities, k, dim=1)
        
        results = []
        for prob, idx in zip(top_probs[0], top_indices[0]):
            class_id = idx.item()
            label = self.class_mapping.get(class_id, 'other')
            results.append((label, prob.item()))
        
        return results


# グローバルインスタンス
classifier = None


def init_classifier(device='cpu'):
    """分類器の初期化"""
    global classifier
    classifier = ImageClassifier(device=device)


def get_classifier():
    """分類器のインスタンスを取得"""
    global classifier
    if classifier is None:
        init_classifier()
    return classifier
