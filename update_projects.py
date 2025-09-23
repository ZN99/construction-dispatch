#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
プロジェクトデータを実際のデータで更新するスクリプト
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Django設定をセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_dispatch.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from order_management.models import Project, ProgressStepTemplate, ProjectProgressStep
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def parse_date(date_str):
    """日付文字列をdateオブジェクトに変換"""
    if not date_str or date_str == '' or date_str == 'null':
        return None
    try:
        # 2025/06/10 形式
        if '/' in date_str:
            return datetime.strptime(date_str, '%Y/%m/%d').date()
        # その他のケース
        return None
    except:
        return None

def parse_amount(amount_str):
    """金額文字列をDecimalに変換"""
    if not amount_str or amount_str == '' or amount_str == '¥0':
        return Decimal('0')
    try:
        # ¥記号とカンマを除去
        cleaned = amount_str.replace('¥', '').replace(',', '').replace('-', '')
        return Decimal(cleaned)
    except:
        return Decimal('0')

# プロジェクトデータ
projects_data = [
    {
        'site_name': '東京タワー展望デッキ改修工事',
        'site_address': '東京都港区芝公園4丁目2-8',
        'work_type': '総合',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/10',
        'contractor_name': '大成建設株式会社',
        'contractor_address': '東京都新宿区西新宿1-25-1',
        'payment_due_date': '2025/03/31',
        'work_start_date': '2025/02/01',
        'work_end_date': '2025/03/20',
        'estimated_amount': '¥15,000,000'
    },
    {
        'site_name': '横浜赤レンガ倉庫 耐震補強工事',
        'site_address': '神奈川県横浜市中区新港1-1',
        'work_type': '土木',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/15',
        'contractor_name': '鹿島建設株式会社',
        'contractor_address': '東京都港区元赤坂1-3-1',
        'payment_due_date': '2025/06/30',
        'work_start_date': '2025/03/01',
        'work_end_date': '2025/05/31',
        'estimated_amount': '¥45,000,000'
    },
    {
        'site_name': '渋谷スクランブルスクエア 外壁塗装工事',
        'site_address': '東京都渋谷区渋谷2-24-12',
        'work_type': '塗装',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/01',
        'contractor_name': '清水建設株式会社',
        'contractor_address': '東京都中央区京橋2-16-1',
        'payment_due_date': '2025/04/30',
        'work_start_date': '2025/03/15',
        'work_end_date': '2025/04/20',
        'estimated_amount': '¥8,500,000'
    },
    {
        'site_name': '新国立競技場 メンテナンス工事',
        'site_address': '東京都新宿区霞ヶ丘町10-1',
        'work_type': '設備',
        'order_status': 'NG',
        'estimate_issued_date': '',
        'contractor_name': '竹中工務店株式会社',
        'contractor_address': '大阪府大阪市中央区本町4-1-13',
        'payment_due_date': '',
        'work_start_date': '',
        'work_end_date': '',
        'estimated_amount': '¥0'
    },
    {
        'site_name': '羽田空港第3ターミナル拡張工事',
        'site_address': '東京都大田区羽田空港2-6-5',
        'work_type': '総合',
        'order_status': '検討中',
        'estimate_issued_date': '',
        'contractor_name': '大林組株式会社',
        'contractor_address': '東京都港区港南2-15-2',
        'payment_due_date': '',
        'work_start_date': '',
        'work_end_date': '',
        'estimated_amount': '¥0'
    },
    {
        'site_name': 'さいたまスーパーアリーナ 照明設備更新',
        'site_address': '埼玉県さいたま市中央区新都心8',
        'work_type': '電気',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/10',
        'contractor_name': '関電工株式会社',
        'contractor_address': '東京都港区芝浦4-8-33',
        'payment_due_date': '2025/05/31',
        'work_start_date': '2025/04/01',
        'work_end_date': '2025/05/15',
        'estimated_amount': '¥12,000,000'
    },
    {
        'site_name': '東京ディズニーランド 新アトラクション建設',
        'site_address': '千葉県浦安市舞浜1-1',
        'work_type': '総合',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/20',
        'contractor_name': '五洋建設株式会社',
        'contractor_address': '東京都文京区後楽2-2-8',
        'payment_due_date': '2025/12/31',
        'work_start_date': '2025/04/01',
        'work_end_date': '2025/11/30',
        'estimated_amount': '¥250,000,000'
    },
    {
        'site_name': '六本木ヒルズ エレベーター更新工事',
        'site_address': '東京都港区六本木6-10-1',
        'work_type': '設備',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/15',
        'contractor_name': '三菱電機ビルソリューションズ株式会社',
        'contractor_address': '東京都千代田区丸の内2-7-3',
        'payment_due_date': '2025/06/30',
        'work_start_date': '2025/05/01',
        'work_end_date': '2025/06/15',
        'estimated_amount': '¥35,000,000'
    },
    {
        'site_name': '品川駅高輪ゲートウェイ 連絡通路建設',
        'site_address': '東京都港区港南2-13-34',
        'work_type': '土木',
        'order_status': '受注',
        'estimate_issued_date': '2025/01/25',
        'contractor_name': 'JR東日本建設株式会社',
        'contractor_address': '東京都渋谷区代々木2-2-2',
        'payment_due_date': '2025/09/30',
        'work_start_date': '2025/05/01',
        'work_end_date': '2025/08/31',
        'estimated_amount': '¥68,000,000'
    },
    {
        'site_name': 'イオンレイクタウン 増床工事',
        'site_address': '埼玉県越谷市レイクタウン4-2-2',
        'work_type': '総合',
        'order_status': '受注',
        'estimate_issued_date': '2025/02/20',
        'contractor_name': 'イオンディライト株式会社',
        'contractor_address': '大阪府大阪市中央区南船場2-3-2',
        'payment_due_date': '2025/08/31',
        'work_start_date': '2025/06/01',
        'work_end_date': '2025/08/15',
        'estimated_amount': '¥95,000,000'
    },
    {
        'site_name': '千葉みなと駅前再開発ビル建設',
        'site_address': '千葉県千葉市中央区中央港1-20-1',
        'work_type': '総合',
        'order_status': '受注',
        'estimate_issued_date': '2025/03/01',
        'contractor_name': '戸田建設株式会社',
        'contractor_address': '東京都中央区八丁堀2-8-5',
        'payment_due_date': '2026/03/31',
        'work_start_date': '2025/07/01',
        'work_end_date': '2026/02/28',
        'estimated_amount': '¥380,000,000'
    },
    {
        'site_name': '浅草寺 五重塔修復工事',
        'site_address': '東京都台東区浅草2-3-1',
        'work_type': '文化財',
        'order_status': '受注',
        'estimate_issued_date': '2025/03/10',
        'contractor_name': '松井建設株式会社',
        'contractor_address': '東京都中央区新川1-17-22',
        'payment_due_date': '2025/10/31',
        'work_start_date': '2025/07/01',
        'work_end_date': '2025/10/15',
        'estimated_amount': '¥125,000,000'
    },
    {
        'site_name': '横浜ランドマークタワー 空調設備更新',
        'site_address': '神奈川県横浜市西区みなとみらい2-2-1',
        'work_type': '設備',
        'order_status': 'NG',
        'estimate_issued_date': '',
        'contractor_name': '高砂熱学工業株式会社',
        'contractor_address': '東京都新宿区新宿6-27-30',
        'payment_due_date': '',
        'work_start_date': '',
        'work_end_date': '',
        'estimated_amount': '¥0'
    },
    {
        'site_name': 'お台場アクアシティ 防水工事',
        'site_address': '東京都港区台場1-7-1',
        'work_type': '防水',
        'order_status': '受注',
        'estimate_issued_date': '2025/03/15',
        'contractor_name': '東レ建設株式会社',
        'contractor_address': '大阪府大阪市北区中之島3-3-3',
        'payment_due_date': '2025/07/31',
        'work_start_date': '2025/06/01',
        'work_end_date': '2025/07/15',
        'estimated_amount': '¥28,000,000'
    },
    {
        'site_name': '池袋サンシャインシティ リニューアル工事',
        'site_address': '東京都豊島区東池袋3-1',
        'work_type': '内装',
        'order_status': '受注',
        'estimate_issued_date': '2025/03/20',
        'contractor_name': '株式会社乃村工藝社',
        'contractor_address': '東京都港区台場2-3-4',
        'payment_due_date': '2025/09/30',
        'work_start_date': '2025/07/15',
        'work_end_date': '2025/09/15',
        'estimated_amount': '¥58,000,000'
    },
    {
        'site_name': '川越駅西口再開発 商業施設建設',
        'site_address': '埼玉県川越市脇田本町8-1',
        'work_type': '総合',
        'order_status': 'NG',
        'estimate_issued_date': '',
        'contractor_name': '西松建設株式会社',
        'contractor_address': '東京都港区虎ノ門1-23-1',
        'payment_due_date': '',
        'work_start_date': '',
        'work_end_date': '',
        'estimated_amount': '¥0'
    },
    {
        'site_name': '成田空港第1ターミナル 改修工事',
        'site_address': '千葉県成田市成田国際空港内',
        'work_type': '総合',
        'order_status': '検討中',
        'estimate_issued_date': '',
        'contractor_name': '前田建設工業株式会社',
        'contractor_address': '東京都千代田区富士見2-10-2',
        'payment_due_date': '',
        'work_start_date': '',
        'work_end_date': '',
        'estimated_amount': '¥0'
    },
    {
        'site_name': '東京スカイツリー 照明システム更新',
        'site_address': '東京都墨田区押上1-1-2',
        'work_type': '電気',
        'order_status': '受注',
        'estimate_issued_date': '2025/04/01',
        'contractor_name': 'パナソニック株式会社エレクトリックワークス社',
        'contractor_address': '大阪府門真市大字門真1048',
        'payment_due_date': '2025/08/31',
        'work_start_date': '2025/07/01',
        'work_end_date': '2025/08/15',
        'estimated_amount': '¥42,000,000'
    },
    {
        'site_name': '富士山五合目 レストハウス改築',
        'site_address': '山梨県富士吉田市上吉田',
        'work_type': '総合',
        'order_status': '受注',
        'estimate_issued_date': '2025/04/10',
        'contractor_name': '株式会社フジタ',
        'contractor_address': '東京都渋谷区千駄ヶ谷4-25-2',
        'payment_due_date': '2025/10/31',
        'work_start_date': '2025/08/01',
        'work_end_date': '2025/10/15',
        'estimated_amount': '¥185,000,000'
    },
    {
        'site_name': '横浜中華街 関帝廟修復工事',
        'site_address': '神奈川県横浜市中区山下町140',
        'work_type': '文化財',
        'order_status': '受注',
        'estimate_issued_date': '2025/04/15',
        'contractor_name': '東急建設株式会社',
        'contractor_address': '東京都渋谷区渋谷1-16-14',
        'payment_due_date': '2025/09/30',
        'work_start_date': '2025/07/15',
        'work_end_date': '2025/09/15',
        'estimated_amount': '¥75,000,000'
    },
    {
        'site_name': '大宮ソニックシティ 外壁改修工事',
        'site_address': '埼玉県さいたま市大宮区桜木町1-7-5',
        'work_type': '外装',
        'order_status': '受注',
        'estimate_issued_date': '2025/04/20',
        'contractor_name': '株式会社熊谷組',
        'contractor_address': '東京都新宿区津久戸町2-1',
        'payment_due_date': '2025/11/30',
        'work_start_date': '2025/09/01',
        'work_end_date': '2025/11/15',
        'estimated_amount': '¥145,000,000'
    },
    {
        'site_name': '新宿バルト9 シアター改装工事',
        'site_address': '東京都新宿区新宿3-1-26',
        'work_type': '内装',
        'order_status': '受注',
        'estimate_issued_date': '2025/05/01',
        'contractor_name': 'TOHOシネマズ株式会社',
        'contractor_address': '東京都千代田区有楽町1-2-2',
        'payment_due_date': '2025/09/30',
        'work_start_date': '2025/08/01',
        'work_end_date': '2025/09/15',
        'estimated_amount': '¥88,000,000'
    },
    {
        'site_name': '幕張メッセ 国際展示場改修',
        'site_address': '千葉県千葉市美浜区中瀬2-1',
        'work_type': '総合',
        'order_status': '受注',
        'estimate_issued_date': '2025/05/10',
        'contractor_name': '株式会社錢高組',
        'contractor_address': '大阪府大阪市西区西本町2-2-4',
        'payment_due_date': '2025/12/31',
        'work_start_date': '2025/10/01',
        'work_end_date': '2025/12/15',
        'estimated_amount': '¥220,000,000'
    },
    {
        'site_name': 'みなとみらい21 新オフィスビル建設',
        'site_address': '神奈川県横浜市西区みなとみらい4-4-5',
        'work_type': '総合',
        'order_status': '受注',
        'estimate_issued_date': '2025/05/15',
        'contractor_name': '三井住友建設株式会社',
        'contractor_address': '東京都中央区佃2-1-6',
        'payment_due_date': '2026/06/30',
        'work_start_date': '2025/09/01',
        'work_end_date': '2026/05/31',
        'estimated_amount': '¥850,000,000'
    },
    {
        'site_name': '浦和レッズスタジアム 芝生張替え工事',
        'site_address': '埼玉県さいたま市緑区美園2-1',
        'work_type': '土木',
        'order_status': '受注',
        'estimate_issued_date': '2025/05/20',
        'contractor_name': '東洋グリーン株式会社',
        'contractor_address': '東京都中央区日本橋小舟町7-4',
        'payment_due_date': '2025/08/31',
        'work_start_date': '2025/07/20',
        'work_end_date': '2025/08/10',
        'estimated_amount': '¥32,000,000'
    }
]

def create_progress_steps(project, order_status, work_start_completed, work_end_completed, invoice_issued, survey_required):
    """プロジェクトの進捗ステップを作成"""
    if order_status != '受注':
        return

    # 基本的なステップテンプレートを取得または作成
    estimate_template, _ = ProgressStepTemplate.objects.get_or_create(
        name='見積書発行',
        defaults={'icon': 'fas fa-calculator', 'order': 1, 'is_default': True}
    )

    contract_template, _ = ProgressStepTemplate.objects.get_or_create(
        name='契約',
        defaults={'icon': 'fas fa-handshake', 'order': 2, 'is_default': True}
    )

    survey_template = None
    if survey_required:
        survey_template, _ = ProgressStepTemplate.objects.get_or_create(
            name='現地調査',
            defaults={'icon': 'fas fa-search-location', 'order': 3}
        )

    work_start_template, _ = ProgressStepTemplate.objects.get_or_create(
        name='工事開始',
        defaults={'icon': 'fas fa-play', 'order': 4, 'is_default': True}
    )

    work_end_template, _ = ProgressStepTemplate.objects.get_or_create(
        name='工事終了',
        defaults={'icon': 'fas fa-flag-checkered', 'order': 5, 'is_default': True}
    )

    invoice_template, _ = ProgressStepTemplate.objects.get_or_create(
        name='請求書発行',
        defaults={'icon': 'fas fa-file-invoice', 'order': 6, 'is_default': True}
    )

    # 進捗ステップを作成
    order = 1

    # 見積書発行（常に完了済み）
    ProjectProgressStep.objects.create(
        project=project,
        template=estimate_template,
        order=order,
        is_active=True,
        is_completed=True,
        completed_date=timezone.now() - timedelta(days=random.randint(30, 60))
    )
    order += 1

    # 契約（常に完了済み）
    ProjectProgressStep.objects.create(
        project=project,
        template=contract_template,
        order=order,
        is_active=True,
        is_completed=True,
        completed_date=timezone.now() - timedelta(days=random.randint(20, 40))
    )
    order += 1

    # 現地調査（必要な場合のみ）
    if survey_required and survey_template:
        survey_completed = project.survey_status == 'completed'
        ProjectProgressStep.objects.create(
            project=project,
            template=survey_template,
            order=order,
            is_active=True,
            is_completed=survey_completed,
            completed_date=timezone.now() - timedelta(days=random.randint(10, 20)) if survey_completed else None
        )
        order += 1

    # 工事開始
    ProjectProgressStep.objects.create(
        project=project,
        template=work_start_template,
        order=order,
        is_active=True,
        is_completed=work_start_completed,
        completed_date=timezone.now() - timedelta(days=random.randint(1, 10)) if work_start_completed else None
    )
    order += 1

    # 工事終了
    ProjectProgressStep.objects.create(
        project=project,
        template=work_end_template,
        order=order,
        is_active=True,
        is_completed=work_end_completed,
        completed_date=timezone.now() - timedelta(days=random.randint(0, 5)) if work_end_completed else None
    )
    order += 1

    # 請求書発行
    ProjectProgressStep.objects.create(
        project=project,
        template=invoice_template,
        order=order,
        is_active=True,
        is_completed=invoice_issued,
        completed_date=timezone.now() - timedelta(days=random.randint(0, 3)) if invoice_issued else None
    )

def update_projects():
    """プロジェクトデータを更新"""

    # 既存のプロジェクトを全て削除
    print("既存のプロジェクトを削除中...")
    Project.objects.all().delete()

    # 新しいプロジェクトを作成
    print("新しいプロジェクトを作成中...")
    created_count = 0

    for i, data in enumerate(projects_data, 1):
        # 受注状態の変換（モデルの選択肢に合わせる）
        if data['order_status'] == '受注':
            order_status = '受注'
        elif data['order_status'] == 'NG':
            order_status = 'NG'
        else:
            order_status = '検討中'

        # 現地調査の設定（ランダムに設定）
        survey_required = random.choice([True, False]) if order_status == '受注' else False
        survey_status = 'not_required'
        if survey_required:
            survey_status = random.choice(['required', 'scheduled', 'in_progress', 'completed'])

        # 工事完了状態の判定
        work_start_completed = False
        work_end_completed = False

        # より現実的な進捗を設定
        today = date.today()
        if data['work_start_date'] and parse_date(data['work_start_date']):
            start_date = parse_date(data['work_start_date'])
            if start_date <= today:
                work_start_completed = True
                # 工事期間の一部を完了済みにする場合
                if data['work_end_date'] and parse_date(data['work_end_date']):
                    end_date = parse_date(data['work_end_date'])
                    total_days = (end_date - start_date).days
                    if total_days > 0:
                        # 30%の確率で工事を完了済みにする
                        if random.random() < 0.3 or end_date <= today:
                            work_end_completed = True

        # 請求書発行状態（工事完了していれば請求書も発行済みとする）
        invoice_issued = work_end_completed

        # 管理番号の生成
        management_no = f"2025-{i:04d}"

        try:
            project = Project.objects.create(
                management_no=management_no,
                site_name=data['site_name'],
                site_address=data['site_address'] or '',
                work_type=data['work_type'] or '総合',
                order_status=order_status,

                # 業者情報（文字列フィールド）
                contractor_name=data['contractor_name'] or '',
                contractor_address=data['contractor_address'] or '',
                project_manager='担当者',  # デフォルト値

                # 日付フィールド
                estimate_issued_date=parse_date(data['estimate_issued_date']),
                contract_date=parse_date(data['estimate_issued_date']) if order_status == '受注' else None,
                work_start_date=parse_date(data['work_start_date']),
                work_end_date=parse_date(data['work_end_date']),
                payment_due_date=parse_date(data['payment_due_date']),

                # 金額フィールド（正しいフィールド名）
                estimate_amount=parse_amount(data['estimated_amount']),
                billing_amount=parse_amount(data['estimated_amount']) if invoice_issued else Decimal('0'),
                parking_fee=Decimal('0'),  # デフォルト値

                # 完了フラグ
                work_start_completed=work_start_completed,
                work_end_completed=work_end_completed,
                invoice_issued=invoice_issued,

                # 現地調査関連
                survey_required=survey_required,
                survey_status=survey_status,

                # 見積書不要フラグ（見積発行日がない受注案件は見積不要とする）
                estimate_not_required=(not data['estimate_issued_date'] and order_status == '受注'),

                # 備考
                notes=''  # 簡潔にする
            )
            # 進捗ステップの作成
            create_progress_steps(project, order_status, work_start_completed, work_end_completed, invoice_issued, survey_required)

            created_count += 1
            print(f"✓ {project.site_name} (管理番号: {project.management_no}) - 進捗: {project.get_work_progress_percentage()}%")

        except Exception as e:
            print(f"✗ {data['site_name']} の作成に失敗: {str(e)}")

    print(f"\n完了: {created_count}件のプロジェクトを作成しました。")

if __name__ == '__main__':
    update_projects()