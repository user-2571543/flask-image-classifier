import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os


class ImageClassifier:
    """ResNet18を使用した画像分類モデル"""
    
    def __init__(self, device='cpu'):
        """
        Args:
            device (str): 'cpu' or 'cuda'
        """
        self.device = device
        
        # ResNet18の読み込み（ImageNet学習済みモデル）
        self.model = models.resnet18(pretrained=True)
        self.model.to(device)
        self.model.eval()
        
        # 入力変換パイプライン
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        
        # ImageNet クラスのサブセット（dog, cat, otherに分類）
        self.imagenet_classes = self._load_imagenet_classes()
        self.class_mapping = self._create_class_mapping()
    
    def _load_imagenet_classes(self):
        """ImageNet クラス名の読み込み"""
        # 簡略化: よく使われるクラスを定義
        dog_classes = {
            151: 'Chihuahua', 152: 'Maltese_dog', 153: 'Poodle',
            154: 'Afghan_hound', 155: 'Basset_hound', 156: 'Beagle',
            157: 'Bloodhound', 158: 'Bluetick_coonhound', 159: 'Black_and_tan_coonhound',
            160: 'Treeing_Tennessee_Brindle', 161: 'Redbone', 162: 'Fawn-colored_Weimaraner',
            163: 'Dhole', 164: 'Dingo', 165: 'African_hunting_dog', 166: 'Hyena',
            167: 'Red_wolf', 168: 'Jackal', 169: 'Timber_wolf'
        }
        
        cat_classes = {
            281: 'Tabby', 282: 'Tiger_cat', 283: 'Persian_cat', 284: 'Siamese_cat',
            285: 'Egyptian_cat', 286: 'Cougar', 287: 'Lynx', 288: 'Leopard',
            289: 'Snow_leopard', 290: 'Jaguar', 291: 'Lion', 292: 'Tiger',
            293: 'Cheetah', 294: 'Brown_bear', 295: 'American_black_bear'
        }
        
        return {'dog': dog_classes, 'cat': cat_classes}
    
    def _create_class_mapping(self):
        """ImageNetクラスIDを dog/cat/other に変換するマッピング"""
        mapping = {}
        for label, classes in self.imagenet_classes.items():
            for class_id in classes.keys():
                mapping[class_id] = label
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
        
        return label, confidence


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
