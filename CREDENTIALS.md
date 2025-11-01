# 🔐 システムログイン情報

## 本番環境アカウント

### 1. スーパー管理者アカウント

**全システムアクセス可能**

```
ユーザー名: superadmin
パスワード: ConstructionAdmin2024!
メール: admin@construction.com
```

**アクセス可能なシステム:**
- ✅ Django管理画面 (`/admin/`)
- ✅ 案件管理システム (`/orders/`)
- ✅ 現地調査システム (`/surveys/field/`)
- ✅ 会計ダッシュボード (`/accounting/`)
- ✅ その他すべてのシステム

---

### 2. 調査員アカウント

**現地調査システム専用**

#### 佐藤 花子
```
ユーザー名: sato
パスワード: Survey2024!
メール: sato@construction.com
```

#### 田中 太郎
```
ユーザー名: tanaka
パスワード: Survey2024!
メール: tanaka@construction.com
```

**アクセス可能なシステム:**
- ✅ 現地調査システム (`/surveys/field/`)
- ✅ 案件詳細閲覧

---

## セットアップ方法

### ローカル環境
```bash
cd construction_dispatch
python setup_production_users.py
```

### 本番環境（Render）
1. Render Dashboardにログイン
2. `construction-dispatch` サービスを選択
3. **Shell** タブを開く
4. 以下のコマンドを実行:
```bash
python setup_production_users.py
```

---

## 管理コマンド

### 個別ユーザー作成
```bash
python manage.py create_super_admin <username> <email> <password>
```

### パスワードリセット
```bash
python manage.py reset_password <username> <new_password>
```

---

## セキュリティ注意事項

⚠️ **重要**:
- このファイルは `.gitignore` に追加されています
- 本番環境では必ず強力なパスワードに変更してください
- 定期的にパスワードを変更してください
- 使用していないアカウントは無効化してください

---

## ログインURL

### ローカル環境
```
http://localhost:8000/accounts/login/
```

### 本番環境
```
https://construction-dispatch.onrender.com/accounts/login/
```

---

## トラブルシューティング

### ログインできない場合

1. **ブラウザキャッシュをクリア**
   - Chrome/Edge: `Cmd+Shift+R` (Mac) / `Ctrl+Shift+R` (Windows)
   - Firefox: `Cmd+Shift+R` (Mac) / `Ctrl+F5` (Windows)

2. **パスワードをリセット**
   ```bash
   python manage.py reset_password superadmin ConstructionAdmin2024!
   ```

3. **ユーザーが存在するか確認**
   ```bash
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.filter(username='superadmin').exists()
   ```

---

最終更新日: 2025-11-01
