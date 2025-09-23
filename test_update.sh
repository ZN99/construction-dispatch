#!/bin/bash

# Get fresh session and CSRF token
curl -s -c cookies.txt "http://localhost:8000/orders/86/update/" > /dev/null
CSRF_TOKEN=$(curl -s -b cookies.txt "http://localhost:8000/orders/86/update/" | grep csrfmiddlewaretoken | sed 's/.*value="\([^"]*\)".*/\1/')

# Submit form with all required fields
curl -s -b cookies.txt -X POST "http://localhost:8000/orders/86/update/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "csrfmiddlewaretoken=$CSRF_TOKEN&site_name=浦和レッズスタジアム 芝生張替え工事 TEST&work_type=土木&site_address=埼玉県さいたま市緑区美園2-1&contractor_name=テスト業者&contractor_address=テストアドレス&project_manager=担当者&estimate_amount=32000000&parking_fee=0&expense_amount_1=0&expense_amount_2=0&contract_date=2025-09-22&estimate_issued_date=2025-09-19&order_status=受注" \
  -L -w "%{http_code}|%{url_effective}" -o final_response.html

rm -f cookies.txt
