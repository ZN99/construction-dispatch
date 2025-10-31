#!/usr/bin/env bash
# Renderデプロイ時の自動実行スクリプト

set -o errexit  # エラーがあったら停止

echo "📦 依存関係をインストール中..."
pip install -r requirements.txt

echo "📊 静的ファイルを収集中..."
python manage.py collectstatic --noinput

echo "🔄 データベースマイグレーション実行中..."
python manage.py migrate --noinput

# テストデータの生成（既にデータがある場合はスキップ）
echo "🗄️ データベースの状態を確認中..."
PROJECT_COUNT=$(python manage.py shell -c "from order_management.models import Project; print(Project.objects.count())" 2>/dev/null | tail -n 1 || echo "0")

if [ "$PROJECT_COUNT" -eq "0" ] 2>/dev/null; then
    echo "📁 データベースが空です。包括的なテストデータを生成します..."
    python manage.py load_comprehensive_test_data --count 120
    echo "✅ テストデータ生成完了！"
else
    echo "ℹ️ 既に $PROJECT_COUNT 件の案件データがあります。"
    echo "ℹ️ テストデータ生成をスキップします。"
    echo ""
    echo "💡 データをリセットしたい場合は、Renderのシェルで以下を実行："
    echo "   python manage.py load_comprehensive_test_data --clear --count 120"
fi

echo ""
echo "🎉 ビルド完了！デプロイ準備ができました。"