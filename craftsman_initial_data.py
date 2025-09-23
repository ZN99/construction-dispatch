#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Djangoの設定をロード
sys.path.append("/Users/zainkhalid/Dev/prototype-20250915/construction_dispatch")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "construction_dispatch.settings")
django.setup()

from projects.models import (
    Craftsman,
    CraftsmanSchedule,
    Assignment,
    CraftsmanRating,
    Project,
    ProjectType,
    Customer,
    Surveyor,
)


def create_craftsman_data():
    print("職人のダミーデータを作成中...")

    # 職人データ
    craftsmen_data = [
        {
            "name": "ダミー 太郎",
            "phone": "090-1234-5678",
            "email": "dummy.taro@demo.example.com",
            "line_id": "tanaka_craftsman",
            "skill_level": 4,
            "hourly_rate": 3500,
            "coverage_areas": "テスト県デモ市,サンプル市,架空市",
            "is_active": True,
            "bio": "ベテラン大工。木造住宅の新築・リフォームが得意。15年の経験を持つ。",
            "total_jobs": 120,
            "average_rating": 4.5,
        },
        {
            "name": "サンプル 花子",
            "phone": "090-2345-6789",
            "email": "sample.hanako@demo.example.com",
            "line_id": "",
            "skill_level": 3,
            "hourly_rate": 3200,
            "coverage_areas": "ダミー県テスト市,架空市,サンプル市",
            "is_active": True,
            "bio": "電気工事士1種所持。住宅・商業施設の電気工事に対応。8年の経験。",
            "total_jobs": 85,
            "average_rating": 4.2,
        },
        {
            "name": "テスト 一郎",
            "phone": "090-3456-7890",
            "email": "test.ichiro@demo.example.com",
            "line_id": "suzuki_plumber",
            "skill_level": 4,
            "hourly_rate": 3300,
            "coverage_areas": "サンプル県デモ市,テスト市,架空市",
            "is_active": True,
            "bio": "給排水工事のエキスパート。緊急対応も可能。12年の経験。",
            "total_jobs": 95,
            "average_rating": 4.7,
        },
        {
            "name": "フェイク 美咲",
            "phone": "090-4567-8901",
            "email": "fake.misaki@demo.example.com",
            "line_id": "",
            "skill_level": 3,
            "hourly_rate": 2800,
            "coverage_areas": "テスト県サンプル市,デモ市,架空市",
            "is_active": True,
            "bio": "クロス貼り、床材施工が専門。丁寧な仕上がりに定評。6年の経験。",
            "total_jobs": 65,
            "average_rating": 4.3,
        },
        {
            "name": "デモ 健太",
            "phone": "090-5678-9012",
            "email": "demo.kenta@demo.example.com",
            "line_id": "yamada_exterior",
            "skill_level": 3,
            "hourly_rate": 3100,
            "coverage_areas": "ダミー県テスト市,サンプル市",
            "is_active": True,
            "bio": "外壁塗装、屋根工事が得意。足場組み立ても対応可能。10年の経験。",
            "total_jobs": 75,
            "average_rating": 4.1,
        },
        {
            "name": "アレコレ 修",
            "phone": "090-6789-0123",
            "email": "arekore.osamu@demo.example.com",
            "line_id": "",
            "skill_level": 5,
            "hourly_rate": 3800,
            "coverage_areas": "サンプル県デモ市,架空市,テスト市",
            "is_active": False,
            "bio": "伝統的な左官技術に精通。現在休業中（家族の介護のため）。20年の経験。",
            "total_jobs": 200,
            "average_rating": 4.8,
        },
        {
            "name": "コレナニ 雅子",
            "phone": "090-7890-1234",
            "email": "korenani.masako@demo.example.com",
            "line_id": "",
            "skill_level": 3,
            "hourly_rate": 2900,
            "coverage_areas": "千葉県船橋市,市川市,浦安市",
            "is_active": True,
            "bio": "キッチン・バスルームのタイル工事が専門。9年の経験。",
            "total_jobs": 55,
            "average_rating": 4.4,
        },
        {
            "name": "中村 正樹",
            "phone": "090-8901-2345",
            "email": "nakamura@example.com",
            "line_id": "",
            "skill_level": 2,
            "hourly_rate": 2600,
            "coverage_areas": "埼玉県さいたま市,川越市,所沢市",
            "is_active": True,
            "bio": "住宅解体、部分解体に対応。廃材処理も一括対応。5年の経験。",
            "total_jobs": 40,
            "average_rating": 3.9,
        },
        {
            "name": "ホゲホゲ 純一",
            "phone": "090-9012-3456",
            "email": "hogehoge.junichi@demo.example.com",
            "line_id": "kobayashi_waterproof",
            "skill_level": 4,
            "hourly_rate": 3400,
            "coverage_areas": "テスト県ダミー市,サンプル市,デモ市",
            "is_active": True,
            "bio": "ベランダ・屋上の防水工事が得意。保証期間10年。11年の経験。",
            "total_jobs": 90,
            "average_rating": 4.6,
        },
        {
            "name": "フガフガ 恵",
            "phone": "090-0123-4567",
            "email": "fugafuga.megumi@demo.example.com",
            "line_id": "",
            "skill_level": 2,
            "hourly_rate": 2200,
            "coverage_areas": "ダミー県架空市,テスト市,サンプル市",
            "is_active": True,
            "bio": "建築現場の清掃、ハウスクリーニングが専門。3年の経験。",
            "total_jobs": 25,
            "average_rating": 4.0,
        },
    ]

    # 職人を作成
    created_craftsmen = []
    for data in craftsmen_data:
        craftsman, created = Craftsman.objects.get_or_create(
            name=data["name"], defaults=data
        )
        if created:
            print(f"職人を作成: {craftsman.name}")

            # specialtiesを追加（ProjectTypeが存在する場合）
            if ProjectType.objects.exists():
                # ランダムに1-3個の専門分野を追加
                import random

                available_types = list(ProjectType.objects.all())
                num_specialties = min(random.randint(1, 3), len(available_types))
                selected_types = random.sample(available_types, num_specialties)
                craftsman.specialties.set(selected_types)
                print(f"  専門分野を設定: {[t.name for t in selected_types]}")
        else:
            print(f"職人は既存: {craftsman.name}")
        created_craftsmen.append(craftsman)

    # スケジュールデータを作成
    print("\nスケジュールデータを作成中...")
    today = timezone.now().date()

    for craftsman in created_craftsmen:
        # 過去1週間から未来3週間のスケジュールを作成
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=21)

        current_date = start_date
        while current_date <= end_date:
            # 80%の確率で稼働可能
            is_available = True
            if current_date.weekday() >= 5:  # 土日
                is_available = False if current_date.weekday() == 6 else True  # 日曜は休み
            else:
                import random

                is_available = random.random() < 0.8

            notes = ""
            if not is_available:
                if current_date.weekday() == 6:
                    notes = "定休日"
                else:
                    notes = random.choice(["体調不良", "別現場対応", "研修参加", "家庭の事情"])

            schedule, created = CraftsmanSchedule.objects.get_or_create(
                craftsman=craftsman,
                date=current_date,
                defaults={"is_available": is_available, "notes": notes},
            )

            current_date += timedelta(days=1)

        print(f"{craftsman.name}のスケジュール作成完了")

    # 評価データも作成
    print("\n評価データを作成中...")

    # Surveyorが存在することを確認
    if Surveyor.objects.exists():
        surveyor = Surveyor.objects.first()

        for craftsman in created_craftsmen[:5]:  # 最初の5人に評価をつける
            # 過去のアサインメントがあると仮定して評価を作成
            rating_data = [
                {
                    "technical_skill": 5,
                    "punctuality": 5,
                    "communication": 4,
                    "work_quality": 5,
                    "comments": "非常に丁寧で技術力も高い。また依頼したい。",
                },
                {
                    "technical_skill": 4,
                    "punctuality": 3,
                    "communication": 3,
                    "work_quality": 4,
                    "comments": "作業は良かったが、連絡がやや遅い時があった。",
                },
                {
                    "technical_skill": 5,
                    "punctuality": 5,
                    "communication": 5,
                    "work_quality": 5,
                    "comments": "期日通りに完璧に仕上げてくれた。",
                },
                {
                    "technical_skill": 4,
                    "punctuality": 4,
                    "communication": 3,
                    "work_quality": 3,
                    "comments": "技術的には問題ないが、現場の整理整頓に課題あり。",
                },
                {
                    "technical_skill": 4,
                    "punctuality": 4,
                    "communication": 4,
                    "work_quality": 4,
                    "comments": "真面目で信頼できる職人さんです。",
                },
            ]

            import random

            # まず仮のAssignmentを作成する必要があります（評価にはassignmentが必要）
            if Project.objects.exists():
                project = Project.objects.first()

                for i in range(random.randint(1, 2)):  # 1-2個の評価
                    # 仮のAssignmentを作成
                    assignment = Assignment.objects.create(
                        project=project,
                        craftsman=craftsman,
                        assigned_by=surveyor,
                        status="completed",
                        scheduled_start_date=timezone.now().date()
                        - timedelta(days=random.randint(10, 90)),
                        scheduled_end_date=timezone.now().date()
                        - timedelta(days=random.randint(1, 10)),
                        estimated_hours=8,
                        offered_rate=craftsman.hourly_rate,
                        contact_method="phone",
                    )

                    rating_info = random.choice(rating_data)
                    rating = CraftsmanRating.objects.create(
                        assignment=assignment,
                        craftsman=craftsman,
                        surveyor=surveyor,
                        technical_skill=rating_info["technical_skill"],
                        punctuality=rating_info["punctuality"],
                        communication=rating_info["communication"],
                        work_quality=rating_info["work_quality"],
                        comments=rating_info["comments"],
                        created_at=timezone.now()
                        - timedelta(days=random.randint(1, 90)),
                    )
                    print(f"{craftsman.name}に評価を追加: {rating.overall_rating}点")

    print(f"\n職人データ作成完了！")
    print(f"作成された職人数: {len(created_craftsmen)}")
    print(f"稼働中職人数: {Craftsman.objects.filter(is_active=True).count()}")


if __name__ == "__main__":
    create_craftsman_data()
