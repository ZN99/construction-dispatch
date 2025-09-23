#!/usr/bin/env python
"""
デフォルトの進捗ステップテンプレートを作成するスクリプト
"""
import os
import sys
import django

# Djangoの設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from order_management.models import ProgressStepTemplate

def create_default_steps():
    """デフォルトの進捗ステップを作成"""

    default_steps = [
        {
            'name': '見積書発行',
            'icon': 'fas fa-file-invoice',
            'order': 10,
            'is_default': True,
            'is_system': True,
            'field_type': 'date'
        },
        {
            'name': '契約',
            'icon': 'fas fa-handshake',
            'order': 20,
            'is_default': True,
            'is_system': True,
            'field_type': 'date'
        },
        {
            'name': '工事開始',
            'icon': 'fas fa-play-circle',
            'order': 30,
            'is_default': True,
            'is_system': True,
            'field_type': 'checkbox'
        },
        {
            'name': '工事終了',
            'icon': 'fas fa-stop-circle',
            'order': 40,
            'is_default': True,
            'is_system': True,
            'field_type': 'checkbox'
        },
        {
            'name': '請求書発行',
            'icon': 'fas fa-receipt',
            'order': 50,
            'is_default': True,
            'is_system': True,
            'field_type': 'select',
            'field_options': {'choices': [('false', '未発行'), ('true', '発行済み')]}
        }
    ]

    # 追加可能なステップ（インベントリ）
    available_steps = [
        {
            'name': '現場調査',
            'icon': 'fas fa-search',
            'order': 100,
            'is_default': False,
            'is_system': False,
            'field_type': 'date'
        },
        {
            'name': '許可申請',
            'icon': 'fas fa-file-signature',
            'order': 110,
            'is_default': False,
            'is_system': False,
            'field_type': 'date'
        },
        {
            'name': '材料発注',
            'icon': 'fas fa-boxes',
            'order': 120,
            'is_default': False,
            'is_system': False,
            'field_type': 'date'
        },
        {
            'name': '安全講習',
            'icon': 'fas fa-hard-hat',
            'order': 130,
            'is_default': False,
            'is_system': False,
            'field_type': 'checkbox'
        },
        {
            'name': '完成検査',
            'icon': 'fas fa-clipboard-check',
            'order': 140,
            'is_default': False,
            'is_system': False,
            'field_type': 'date'
        },
        {
            'name': '引渡し',
            'icon': 'fas fa-key',
            'order': 150,
            'is_default': False,
            'is_system': False,
            'field_type': 'date'
        },
        {
            'name': '保証書発行',
            'icon': 'fas fa-certificate',
            'order': 160,
            'is_default': False,
            'is_system': False,
            'field_type': 'checkbox'
        }
    ]

    all_steps = default_steps + available_steps

    created_count = 0
    for step_data in all_steps:
        step, created = ProgressStepTemplate.objects.get_or_create(
            name=step_data['name'],
            defaults=step_data
        )
        if created:
            print(f"作成: {step.name}")
            created_count += 1
        else:
            print(f"既存: {step.name}")

    print(f"\n合計 {created_count} 個のステップテンプレートを作成しました。")

if __name__ == '__main__':
    create_default_steps()