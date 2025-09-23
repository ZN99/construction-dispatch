#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
資材発注データ作成スクリプト
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Djangoの設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from order_management.models import Project, Contractor

def create_material_data():
    """資材発注データを作成"""

    print("=" * 50)
    print("資材発注データを作成します...")

    # 既存のプロジェクトを取得
    projects = Project.objects.filter(
        contractor_name__isnull=False
    ).exclude(
        contractor_name=''
    )[:25]  # 最初の25件に資材データを作成

    if not projects.exists():
        print("❌ プロジェクトが見つかりません")
        return

    print(f"📊 {projects.count()}件のプロジェクトに資材発注データを作成")

    order_count = 0
    today = date.today()

    # 供給業者リスト
    suppliers = [
        '東京建材株式会社',
        '関東資材センター',
        'マテリアル商事',
        '建築材料卸売センター',
        'ホームセンター大型店'
    ]

    # 資材カテゴリと品目
    material_categories = {
        '内装材': [
            ('クロス材 10m巻', 'ロール', 3500),
            ('床材 フローリング', '㎡', 4800),
            ('天井ボード', '枚', 1200),
            ('巾木', 'm', 850),
            ('モールディング', 'm', 1200)
        ],
        '塗料': [
            ('水性ペイント 白', '缶', 8500),
            ('下地プライマー', 'L', 3200),
            ('シーラー', 'L', 2800),
            ('防カビ塗料', '缶', 12000)
        ],
        '設備': [
            ('LED照明器具', '個', 15000),
            ('コンセント', '個', 1800),
            ('スイッチ', '個', 2200),
            ('換気扇', '台', 25000)
        ],
        '金物': [
            ('ビス各種', '箱', 3500),
            ('アンカーボルト', '本', 450),
            ('金具セット', 'セット', 5600),
            ('ドアハンドル', '個', 8500)
        ],
        '消耗品': [
            ('養生テープ', '巻', 650),
            ('マスカー', '巻', 1200),
            ('ブルーシート', '枚', 2500),
            ('清掃用具セット', 'セット', 3800)
        ]
    }

    # 発注ステータスのパターン
    status_patterns = [
        ('draft', '見積依頼中'),
        ('ordered', '発注済'),
        ('partial', '一部納品'),
        ('delivered', '納品完了'),
        ('cancelled', 'キャンセル')
    ]

    for project in projects:
        # 1-3件の発注を作成
        num_orders = random.randint(1, 3)

        for order_num in range(num_orders):
            # サプライヤーをランダムに選択
            supplier_name = random.choice(suppliers)

            # ステータスをランダムに選択（キャンセルは少なめ）
            status_weights = [20, 30, 20, 25, 5]
            status = random.choices(status_patterns, weights=status_weights)[0]

            # 発注日を設定
            order_date = today - timedelta(days=random.randint(0, 30))

            # 希望納期を設定
            delivery_date = order_date + timedelta(days=random.randint(3, 14))

            # 資材発注を作成
            material_order = MaterialOrder.objects.create(
                project=project,
                order_number=f'MO-{project.management_no}-{order_num+1:02d}',
                supplier_name=supplier_name,
                supplier_contact='担当: 営業部',
                supplier_phone='03-0000-0000',
                order_date=order_date,
                requested_delivery_date=delivery_date,
                delivery_address=project.site_address,
                status=status[0],
                notes=f'{project.site_name}用の資材発注'
            )

            # ステータスに応じて追加情報を設定
            if status[0] in ['partial', 'delivered']:
                material_order.actual_delivery_date = delivery_date + timedelta(days=random.randint(-2, 2))

            # 発注明細を作成（3-8品目）
            num_items = random.randint(3, 8)
            total_amount = Decimal('0')

            # ランダムにカテゴリを選択
            selected_categories = random.sample(list(material_categories.keys()), min(3, len(material_categories)))

            item_order = 1
            for category in selected_categories:
                items = material_categories[category]
                selected_items = random.sample(items, min(num_items // len(selected_categories) + 1, len(items)))

                for item_name, unit, base_price in selected_items:
                    quantity = Decimal(random.randint(1, 20))
                    unit_price = Decimal(base_price) * Decimal(random.uniform(0.9, 1.1))
                    unit_price = unit_price.quantize(Decimal('1'))
                    amount = quantity * unit_price

                    MaterialOrderItem.objects.create(
                        material_order=material_order,
                        item_name=item_name,
                        item_code=f'MAT-{random.randint(1000, 9999)}',
                        category=category,
                        quantity=quantity,
                        unit=unit,
                        unit_price=unit_price,
                        amount=amount,
                        order=item_order,
                        notes=''
                    )

                    total_amount += amount
                    item_order += 1

            # 小計と税額を計算
            material_order.subtotal = total_amount
            material_order.tax_amount = (total_amount * Decimal('0.10')).quantize(Decimal('1'))
            material_order.total_amount = material_order.subtotal + material_order.tax_amount

            # 支払い条件を設定
            material_order.payment_terms = random.choice([
                '月末締め翌月末払い',
                '納品後30日以内',
                '請求書到着後14日以内'
            ])

            material_order.save()

            order_count += 1

            status_emoji = {
                'draft': '📝',
                'ordered': '📦',
                'partial': '📤',
                'delivered': '✅',
                'cancelled': '❌'
            }.get(status[0], '❓')

            print(f"  {status_emoji} {project.site_name[:15]}... - ¥{material_order.total_amount:,} ({status[1]})")

    # 統計情報を表示
    print("\n" + "=" * 50)
    print("📊 資材発注データ作成結果:")
    print(f"  発注件数: {order_count}件")
    print(f"  発注明細: {MaterialOrderItem.objects.count()}品目")

    # ステータス別の集計
    for status_code, status_label in status_patterns:
        orders = MaterialOrder.objects.filter(status=status_code)
        count = orders.count()
        if count > 0:
            total = sum(order.total_amount or 0 for order in orders)
            print(f"  {status_label}: {count}件 (¥{total:,})")

    # サプライヤー別の集計
    print(f"\n📦 サプライヤー別:")
    for supplier in suppliers:
        orders = MaterialOrder.objects.filter(supplier_name=supplier)
        count = orders.count()
        if count > 0:
            total = sum(order.total_amount or 0 for order in orders)
            print(f"  {supplier}: {count}件 (¥{total:,})")

    # 総額
    all_orders = MaterialOrder.objects.all()
    grand_total = sum(order.total_amount or 0 for order in all_orders)
    print(f"\n💰 総発注額: ¥{grand_total:,}")

    print("\n✨ 資材発注データの作成が完了しました！")
    print("🌐 確認URL: http://localhost:8000/orders/")


if __name__ == '__main__':
    create_material_data()