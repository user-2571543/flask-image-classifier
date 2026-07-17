# 🖼️ Flask Image Classifier

ResNet18を使用した犬/猫画像分類Webアプリケーション

## 📋 概要

このアプリケーションは、PyTorchのResNet18（ImageNet学習済みモデル）を使用して、ユーザーがアップロードした画像を**犬**・**猫**・**その他**に分類します。

### 主な特徴
- ✅ **ユーザー認証** - Flask-Loginを使用したセキュアなログイン機能
- ✅ **画像アップロード** - ログイン後のみアップロード可能
- ✅ **AI分類** - ResNet18による高精度な画像分類
- ✅ **分類結果の保存** - SQLite DBで分類履歴を管理
- ✅ **画像管理** - アップロード画像と分類結果の表示・削除
- ✅ **レスポンシブデザイン** - Bootstrap5を使用したモダンUI

## 🛠️ 技術スタック

| カテゴリ | 技術 |
|---------|------|
| **フレームワーク** | Flask 2.3.3 |
| **ORM** | SQLAlchemy 3.0.5 |
| **認証** | Flask-Login 0.6.2 |
| **フォーム** | Flask-WTF 1.1.1 |
| **AI モデル** | ResNet18 (torchvision) |
| **UI フレームワーク** | Bootstrap 5.3.0 |

## 📦 セットアップ

### 1. リポジトリのクローン
```bash
git clone https://github.com/user-2571543/flask-image-classifier.git
cd flask-image-classifier
```

### 2. 仮想環境の作成と有効化
```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. データベースの初期化
```bash
flask init-db
```

### 5. (オプション) テスト用ユーザーの作成
```bash
flask seed-db
# ユーザー名: demo
# パスワード: demo1234
```

## 🚀 実行方法

```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください

## 📝 ユーザー登録・ログイン

### 新規ユーザー登録
1. トップページの「登録」をクリック
2. ユーザー名とパスワードを入力
3. 登録完了

### ログイン
1. 「ログイン」ページでユーザー名とパスワードを入力
2. 「ログイン」をクリック

## 🖼️ 機能説明

### アップロード（ログイン必須）
- JPG, PNG, GIF形式に対応（最大16MB）
- ドラッグ&ドロップまたはクリックで画像を選択
- アップロードと同時にAI分類を実行

### 分類結果
- **ラベル**: 犬 / 猫 / その他
- **信頼度**: 分類の確信度（0～100%）

### ギャラリー
- ユーザー別にアップロード画像を表示
- 分類ラベルと信頼度を一覧表示
- ページネーション対応

### 削除（ログイン必須）
- 不要な画像と分類結果をまとめて削除
- 削除操作は取り消せないので要注意

## 📊 データベーススキーマ

### User（ユーザー）
| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer (PK) | ユーザーID |
| username | String | ユーザー名（一意） |
| password_hash | String | パスワードハッシュ |
| created_at | DateTime | 作成日時 |

### UserImage（アップロード画像）
| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer (PK) | 画像ID |
| user_id | Integer (FK) | ユーザーID |
| filename | String | 元のファイル名 |
| upload_path | String | 保存先パス |
| uploaded_at | DateTime | アップロード日時 |

### Prediction（分類結果）
| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer (PK) | 予測ID |
| user_image_id | Integer (FK) | 画像ID |
| label | String | 分類ラベル（dog/cat/other） |
| confidence | Float | 信頼度（0.0～1.0） |
| created_at | DateTime | 作成日時 |

## 🧠 AI モデルについて

### ResNet18
- **学習データ**: ImageNet (100万枚以上の画像)
- **出力**: 1000クラスの確率値
- **用途**: 汎用的な物体認識

### 分類方式
1. ResNet18の出力から確率が最も高いクラスを取得
2. そのクラスIDが犬/猫クラスかチェック
3. 該当する場合は「犬」「猫」、それ以外は「その他」に分類

### 入出力
- **入力**: ユーザーが選択した画像ファイル
- **出力**: 分類ラベル（犬/猫/その他）と信頼度（0～100%）

## 🔐 セキュリティ

- パスワードは bcrypt でハッシュ化
- CSRF 保護（Flask-WTF）
- HTTPOnly Cookieを使用
- SQLインジェクション対策（SQLAlchemy）

## 📸 スクリーンショット

### ログインページ
ユーザー名とパスワードでセキュアにログイン

### アップロードページ
ドラッグ&ドロップで簡単に画像をアップロード

### ギャラリーページ
分類結果を一覧表示し、詳細情報を確認可能

### 詳細ページ
分類結果と信頼度を詳しく表示

## 🐛 トラブルシューティング

### PyTorchのインストールが失敗する
```bash
# CPUのみ版（推奨）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# GPU版（CUDA 11.8）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### ポート5000が既に使用されている
```bash
# 別のポートで実行
python app.py --port 5001
```

### 画像がアップロードできない
- ファイル形式を確認（JPG, PNG, GIF）
- ファイルサイズが16MB以下か確認
- `static/uploads/` ディレクトリが存在することを確認

## 📖 API ドキュメント

### エンドポイント一覧

| メソッド | エンドポイント | 認証 | 説明 |
|---------|----------------|------|------|
| GET | `/` | - | トップページ（ログイン状態に応じてリダイレクト） |
| GET/POST | `/register` | - | ユーザー登録 |
| GET/POST | `/login` | - | ログイン |
| GET | `/logout` | ✅ | ログアウト |
| GET/POST | `/upload` | ✅ | 画像アップロード＆分類 |
| GET | `/gallery` | ✅ | 分類結果一覧 |
| GET | `/image/<id>` | ✅ | 画像詳細表示 |
| POST | `/image/<id>/delete` | ✅ | 画像削除 |

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 👨‍💻 開発者

created by user-2571543

## 📞 サポート

問題が発生した場合は、GitHubのIssueセクションで報告してください。

---

**Happy Image Classifying! 🎉**
