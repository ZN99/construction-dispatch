#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
包括的テストデータ生成スクリプト
全機能をカバーし、データの連動性を確保
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from order_management.models import (
    Project, ProjectFile, Comment, ProjectProgress, ProjectProgressStep,
    Invoice, InvoiceItem, CashFlowTransaction
)
from projects.models import CraftsmanSchedule
from surveys.models import Survey, SurveyPhoto, SurveyRoom, SurveyWall, SurveyDamage

def create_file_attachments():
    """ファイル添付データを作成"""
    print("\n=== 📎 ファイル添付データ作成 ===")

    projects = Project.objects.filter(project_status__in=['進行中', '完工'])[:10]
    admin = User.objects.filter(is_staff=True).first()

    file_types = [
        ('見積書.pdf', 'application/pdf'),
        ('契約書.pdf', 'application/pdf'),
        ('図面.dwg', 'application/dwg'),
        ('施工写真.jpg', 'image/jpeg'),
    ]

    created = 0
    for project in projects:
        num_files = random.randint(1, 3)
        for i in range(num_files):
            file_name, file_type = random.choice(file_types)

            # ダミーファイルコンテンツ
            content = f"Test file for {project.site_name}".encode()

            project_file = ProjectFile.objects.create(
                project=project,
                file_name=file_name,
                file_size=len(content),
                file_type=file_type,
                description=f'{project.site_name}の{file_name}',
                uploaded_by=admin
            )
            # ダミーファイルを保存
            project_file.file.save(file_name, ContentFile(content), save=True)
            created += 1
            print(f"  ✅ {project.site_name} - {file_name}")

    print(f"\n📊 ファイル添付: {created}件作成")
    return created

def create_comments():
    """コメントデータを作成"""
    print("\n=== 💬 コメントデータ作成 ===")

    projects = Project.objects.all()[:15]
    users = list(User.objects.all()[:5])

    comment_templates = [
        "進捗確認しました。順調です。",
        "材料の納品が遅れる可能性があります。",
        "現地で追加工事が必要になりました。",
        "お客様から変更依頼がありました。",
        "完了検査の日程を調整中です。",
    ]

    created = 0
    for project in projects:
        num_comments = random.randint(1, 4)
        for i in range(num_comments):
            Comment.objects.create(
                project=project,
                author=random.choice(users),
                content=random.choice(comment_templates)
            )
            created += 1

    print(f"📊 コメント: {created}件作成")
    return created

def create_progress_records():
    """進捗記録データを作成"""
    print("\n=== 📈 進捗記録データ作成 ===")

    projects = Project.objects.filter(project_status__in=['進行中', '完工'])[:20]

    step_types = [
        ('estimate', '見積提出'),
        ('contract', '契約締結'),
        ('start_work', '着工'),
        ('inspection', '中間検査'),
        ('completion', '完了検査'),
        ('delivery', '引き渡し'),
    ]

    created = 0
    for project in projects:
        # ProjectProgressを作成
        progress, _ = ProjectProgress.objects.get_or_create(
            project=project
        )

        num_steps = random.randint(2, 5)
        for i in range(num_steps):
            step_key, step_name = step_types[min(i, len(step_types)-1)]
            ProjectProgressStep.objects.get_or_create(
                progress=progress,
                step_key=step_key,
                defaults={
                    'step_name': step_name,
                    'order': i,
                    'is_completed': i < num_steps - 1,  # 最後以外は完了
                    'completed_date': date.today() - timedelta(days=random.randint(1, 30)) if i < num_steps - 1 else None,
                }
            )
            created += 1

    print(f"📊 進捗ステップ: {created}件作成")
    return created

def create_survey_photos():
    """調査写真データを作成"""
    print("\n=== 📷 調査写真データ作成 ===")

    surveys = Survey.objects.all()

    photo_types = [
        ('room_overview', '部屋全景'),
        ('damage_detail', '損傷箇所'),
        ('wall_condition', '壁面状態'),
    ]

    created = 0
    for survey in surveys:
        # 各調査に2-4枚の写真を追加
        num_photos = random.randint(2, 4)
        for i in range(num_photos):
            photo_type, caption = random.choice(photo_types)

            # ダミー画像コンテンツ
            content = f"Survey photo for {survey.project.site_name}".encode()

            photo = SurveyPhoto.objects.create(
                survey=survey,
                photo_type=photo_type,
                caption=f'{caption} - {survey.project.site_name}',
            )
            # ダミー画像を保存
            photo.image.save(f'survey_{survey.id}_{i}.jpg', ContentFile(content), save=True)
            created += 1

    print(f"📊 調査写真: {created}件作成")
    return created

def create_invoices():
    """請求書データを作成"""
    print("\n=== 📄 請求書データ作成 ===")

    projects = Project.objects.filter(project_status__in=['進行中', '完工'])[:10]

    created = 0
    # 既存の最大請求書番号を確認
    existing_invoices = Invoice.objects.filter(invoice_number__startswith=f"INV-{date.today().year}").count()
    start_index = existing_invoices + 1

    for i, project in enumerate(projects):
        # 請求書番号を生成（既存のものと被らないように）
        invoice_number = f"INV-{date.today().year}-{str(start_index + i).zfill(4)}"

        # 既に存在する場合はスキップ
        if Invoice.objects.filter(invoice_number=invoice_number).exists():
            continue

        # 日付を設定
        issue_date = date.today() - timedelta(days=random.randint(1, 30))
        due_date = issue_date + timedelta(days=30)

        # 金額計算
        subtotal = project.order_amount if project.order_amount else Decimal('1000000')
        tax_rate = Decimal('10.00')
        tax_amount = subtotal * tax_rate / 100
        total_amount = subtotal + tax_amount

        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            client_name=project.client_name,
            client_address=project.site_address if hasattr(project, 'site_address') else '',
            issue_date=issue_date,
            due_date=due_date,
            billing_period_start=issue_date - timedelta(days=30),
            billing_period_end=issue_date,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status=random.choice(['issued', 'sent', 'paid']),
            notes=f'{project.site_name}の工事代金'
        )

        # 請求書明細を作成
        work_type = project.work_type if hasattr(project, 'work_type') and project.work_type else '工事'
        InvoiceItem.objects.create(
            invoice=invoice,
            project=project,
            description=f'{project.site_name} - {work_type}',
            quantity=1,
            unit_price=subtotal,
            amount=subtotal,
            order=1
        )

        created += 1
        print(f"  ✅ {invoice_number} - {project.client_name}")

    print(f"\n📊 請求書: {created}件作成")
    return created

def verify_data_connections():
    """データ連動性を検証"""
    print("\n=== 🔗 データ連動性検証 ===")

    from order_management.models import MaterialOrder
    from subcontract_management.models import Subcontract

    # 材料発注
    materials = MaterialOrder.objects.all()
    mat_connected = materials.filter(project__isnull=False).count()
    mat_percent = (mat_connected / materials.count() * 100) if materials.count() > 0 else 0
    print(f"材料発注: {mat_connected}/{materials.count()}件が案件に紐づく ({mat_percent:.1f}%)")

    # 外注発注
    subcontracts = Subcontract.objects.all()
    sub_connected = subcontracts.filter(project__isnull=False).count()
    sub_percent = (sub_connected / subcontracts.count() * 100) if subcontracts.count() > 0 else 0
    print(f"外注発注: {sub_connected}/{subcontracts.count()}件が案件に紐づく ({sub_percent:.1f}%)")

    # 現地調査
    surveys = Survey.objects.all()
    survey_connected = surveys.filter(project__isnull=False).count()
    survey_percent = (survey_connected / surveys.count() * 100) if surveys.count() > 0 else 0
    print(f"現地調査: {survey_connected}/{surveys.count()}件が案件に紐づく ({survey_percent:.1f}%)")

    # ファイル添付
    files = ProjectFile.objects.all()
    file_connected = files.filter(project__isnull=False).count()
    file_percent = (file_connected / files.count() * 100) if files.count() > 0 else 0
    print(f"ファイル添付: {file_connected}/{files.count()}件が案件に紐づく ({file_percent:.1f}%)")

    # コメント
    comments = Comment.objects.all()
    comment_connected = comments.filter(project__isnull=False).count()
    comment_percent = (comment_connected / comments.count() * 100) if comments.count() > 0 else 0
    print(f"コメント: {comment_connected}/{comments.count()}件が案件に紐づく ({comment_percent:.1f}%)")

    # 進捗記録
    progress_steps = ProjectProgressStep.objects.all()
    progress_connected = progress_steps.filter(project__isnull=False).count()
    progress_percent = (progress_connected / progress_steps.count() * 100) if progress_steps.count() > 0 else 0
    print(f"進捗ステップ: {progress_connected}/{progress_steps.count()}件が案件に紐づく ({progress_percent:.1f}%)")

    # 入出金データ
    transactions = CashFlowTransaction.objects.all()
    trans_connected = transactions.filter(project__isnull=False).count()
    trans_percent = (trans_connected / transactions.count() * 100) if transactions.count() > 0 else 0
    print(f"キャッシュフロー取引: {trans_connected}/{transactions.count()}件が案件に紐づく ({trans_percent:.1f}%)")

    # 請求書
    invoices = Invoice.objects.all()
    print(f"請求書: {invoices.count()}件作成済み")

    # カレンダー/スケジュール
    schedules = CraftsmanSchedule.objects.all()
    if schedules.count() > 0:
        schedule_with_project = schedules.filter(assigned_project__isnull=False).count()
        schedule_percent = (schedule_with_project / schedules.count() * 100)
        print(f"職人スケジュール: {schedule_with_project}/{schedules.count()}件が案件にアサイン済み ({schedule_percent:.1f}%)")
    else:
        print(f"職人スケジュール: 0件")

    # 調査スケジュール
    surveys_with_schedule = surveys.exclude(scheduled_date__isnull=True).count()
    survey_schedule_percent = (surveys_with_schedule / surveys.count() * 100) if surveys.count() > 0 else 0
    print(f"現地調査（スケジュール設定済み）: {surveys_with_schedule}/{surveys.count()}件 ({survey_schedule_percent:.1f}%)")

    print("\n✅ すべてのデータが正しく連動しています" if all([
        mat_percent == 100, sub_percent == 100, survey_percent == 100,
        file_percent == 100, comment_percent == 100, trans_percent == 100
    ]) else "\n⚠️  一部のデータが孤立しています")

def main():
    print("=" * 60)
    print("包括的テストデータ生成を開始します...")
    print("=" * 60)

    # 各種テストデータを作成
    file_count = create_file_attachments()
    comment_count = create_comments()
    # progress_count = create_progress_records()  # Skip - different model structure
    photo_count = create_survey_photos()
    invoice_count = create_invoices()
    progress_count = 0

    # 連動性を検証
    verify_data_connections()

    print("\n" + "=" * 60)
    print("✨ テストデータ生成完了")
    print("=" * 60)
    print(f"📎 ファイル添付: {file_count}件")
    print(f"💬 コメント: {comment_count}件")
    print(f"📈 進捗記録: {progress_count}件")
    print(f"📷 調査写真: {photo_count}件")
    print(f"📄 請求書: {invoice_count}件")
    print(f"\n🌐 確認URL: http://localhost:8000/orders/projects/")

if __name__ == '__main__':
    main()
