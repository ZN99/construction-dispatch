import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "construction_dispatch.settings")
django.setup()

from projects.models import ProjectType, Customer

# 工種データの初期化
project_types = [
    {"name": "クロス", "description": "壁紙の張り替え作業"},
    {"name": "クリーニング", "description": "清掃作業全般"},
    {"name": "電気工事", "description": "電気設備の工事"},
    {"name": "配管工事", "description": "水道・ガス配管工事"},
    {"name": "内装工事", "description": "内装全般の工事"},
    {"name": "外装工事", "description": "外壁・屋根工事"},
]

for pt_data in project_types:
    project_type, created = ProjectType.objects.get_or_create(
        name=pt_data["name"], defaults={"description": pt_data["description"]}
    )
    if created:
        print(f'工種 "{project_type.name}" を作成しました')
    else:
        print(f'工種 "{project_type.name}" は既に存在します')

# サンプル顧客データ
customers = [
    {
        "name": "田中建設",
        "phone": "03-1234-5678",
        "email": "tanaka@example.com",
        "address": "東京都新宿区西新宿1-1-1",
    },
    {
        "name": "佐藤工務店",
        "phone": "06-9876-5432",
        "email": "sato@example.com",
        "address": "大阪府大阪市中央区難波1-1-1",
    },
    {
        "name": "山田リフォーム",
        "phone": "045-1111-2222",
        "email": "yamada@example.com",
        "address": "神奈川県横浜市西区みなとみらい1-1-1",
    },
]

for customer_data in customers:
    customer, created = Customer.objects.get_or_create(
        name=customer_data["name"],
        defaults={
            "phone": customer_data["phone"],
            "email": customer_data["email"],
            "address": customer_data["address"],
        },
    )
    if created:
        print(f'顧客 "{customer.name}" を作成しました')
    else:
        print(f'顧客 "{customer.name}" は既に存在します')

print("初期データの作成が完了しました！")
