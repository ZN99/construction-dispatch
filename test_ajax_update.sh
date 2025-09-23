#!/bin/bash

echo "Testing AJAX project update..."

# セッションクッキーを取得
curl -s -c cookies.txt "http://localhost:8000/orders/86/update/" > /dev/null

# CSRFトークンを取得
CSRF_TOKEN=$(curl -s -b cookies.txt "http://localhost:8000/orders/86/update/" | grep csrfmiddlewaretoken | sed 's/.*value="\([^"]*\)".*/\1/')

echo "CSRF Token: ${CSRF_TOKEN:0:20}..."

# AJAX形式でプロジェクトを更新
echo "Sending AJAX update request..."
RESPONSE=$(curl -s -b cookies.txt -X POST "http://localhost:8000/orders/86/update/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d "csrfmiddlewaretoken=$CSRF_TOKEN&site_name=浦和レッズスタジアム 芝生張替え工事 AJAX TEST&work_type=土木&site_address=埼玉県さいたま市緑区美園2-1&contractor_company=1&contractor_name=田中建設株式会社&contractor_address=東京都新宿区&project_manager=担当者&estimate_amount=32000000&parking_fee=0&expense_amount_1=0&expense_amount_2=0&contract_date=2025-09-22&estimate_issued_date=2025-09-19&order_status=受注" \
  -w "%{http_code}")

echo "Response: $RESPONSE"

# レスポンスをJSONとして解析
if echo "$RESPONSE" | grep -q '"success": true'; then
    echo "✅ SUCCESS: AJAX update worked!"
    
    # データベースで確認
    echo "Checking database..."
    python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()
from order_management.models import Project
project = Project.objects.get(pk=86)
print('Current site_name:', repr(project.site_name))
if 'AJAX TEST' in project.site_name:
    print('✅ Database updated successfully!')
else:
    print('❌ Database not updated')
"
else
    echo "❌ AJAX update failed"
fi

rm -f cookies.txt
