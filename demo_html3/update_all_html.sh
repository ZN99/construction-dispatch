#!/bin/bash

# ========================================
# 建築派遣SaaS HTMLファイル一括更新スクリプト
# シンプルUIテーマを全画面に適用
# ========================================
#
# 目的:
# - 既存HTMLファイルにシンプルUIテーマを適用
# - Bootstrap IconsをFont Awesomeに統一
# - simple_ui.jsを全画面に追加
# - 一貫したUI/UX体験の提供
#
# 使用方法:
# ./update_all_html.sh
#
# 注意事項:
# - 実行前にファイルのバックアップを推奨
# - sed コマンドを使用するため macOS/Linux 環境が必要
# ========================================

echo "🚀 建築派遣SaaS HTMLファイルをシンプルUIテーマに更新中..."

# 対象HTMLファイルリスト
# シンプルUIテーマを適用する主要なHTMLファイル
files=(
    "pricing/auto_quotation.html"          # SaaS自動見積画面
    "pricing/quotation_adjustment.html"    # 社員用見積調整画面
    "analytics/profit_analysis.html"       # 利益率分析画面
    "settings/margin_settings.html"        # マージン率設定画面
)

# 各ファイルに対してシンプルUIテーマを適用
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "📝 更新中: $file"

        # simple_theme.cssを先頭に追加
        # titleタグの後にCSSリンクを挿入（最優先読み込みのため）
        sed -i.bak '/<title>/a\
    <link rel="stylesheet" href="../css/simple_theme.css">' "$file"

        # Font Awesomeを追加（Bootstrap Iconsの代替）
        # simple_theme.cssの後にFont Awesomeを追加
        sed -i.bak '/<link rel="stylesheet" href=".*simple_theme.css">/a\
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">' "$file"

        # simple_ui.jsを追加
        # Bootstrap JSの前にsimple_ui.jsを挿入（依存関係を考慮）
        sed -i.bak '/bootstrap@5.3.0.*bootstrap.bundle.min.js/i\
    <script src="../js/simple_ui.js"></script>' "$file"

        # Bootstrap Iconsクラスを Font Awesome に一括置換
        # bi bi- → fas fa- に変更（Bootstrap Icons → Font Awesome）
        sed -i.bak 's/bi bi-/fas fa-/g' "$file"
        # bi- → fa- に変更（単体のBootstrap Iconsクラス）
        sed -i.bak 's/bi-/fa-/g' "$file"

        # バックアップファイル削除（.bakファイルのクリーンアップ）
        rm -f "$file.bak"

        echo "✅ 完了: $file"
    else
        echo "❌ ファイルが見つかりません: $file"
    fi
done

echo ""
echo "🎉 HTMLファイルの更新が完了しました！"
echo ""
echo "更新内容:"
echo "- simple_theme.css を全画面に適用"
echo "- simple_ui.js を全画面に追加"
echo "- Bootstrap Icons を Font Awesome に置換"
echo "- シンプルでミニマルなUIに統一"
echo ""
echo "注意:"
echo "- 既存のBootstrapスタイルは互換性のため一部残されています"
echo "- カスタムスタイルが優先されるようCSS読み込み順序を調整済み"
echo ""
echo "次のステップ:"
echo "1. ブラウザで各画面を確認"
echo "2. 必要に応じて個別調整"
echo "3. モバイル表示の確認"