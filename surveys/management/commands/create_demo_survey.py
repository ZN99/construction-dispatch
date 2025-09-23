from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time
from surveys.models import Survey, Surveyor, SurveyRoom
from order_management.models import Project


class Command(BaseCommand):
    help = 'デモ用の調査データを作成'

    def handle(self, *args, **options):
        # 調査員を作成または取得
        surveyor, created = Surveyor.objects.get_or_create(
            employee_id='SV001',
            defaults={
                'name': '田中 太郎',
                'email': 'tanaka@example.com',
                'phone': '090-1234-5678',
                'department': '調査部',
                'specialties': 'クロス張り替え調査, 内装調査',
                'experience_years': 5,
                'is_active': True
            }
        )

        if created:
            self.stdout.write(f'調査員 {surveyor.name} を作成しました')
        else:
            self.stdout.write(f'調査員 {surveyor.name} は既に存在します')

        # プロジェクトを取得（既存のものを使用）
        try:
            project = Project.objects.first()
            if not project:
                self.stdout.write(
                    self.style.ERROR('プロジェクトが見つかりません。先にorder_managementアプリでプロジェクトを作成してください。')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'プロジェクト取得エラー: {e}')
            )
            return

        # 調査を作成
        survey, created = Survey.objects.get_or_create(
            project=project,
            surveyor=surveyor,
            defaults={
                'scheduled_date': date.today(),
                'scheduled_start_time': time(10, 0),
                'estimated_duration': 120,
                'status': 'scheduled',
                'notes': 'クロス張り替え調査のデモ用データ'
            }
        )

        if created:
            self.stdout.write(f'調査 {survey} を作成しました')

            # 部屋データを作成
            room, room_created = SurveyRoom.objects.get_or_create(
                survey=survey,
                room_name='リビング',
            )

            if room_created:
                self.stdout.write(f'調査部屋 {room.room_name} を作成しました')

            self.stdout.write(
                self.style.SUCCESS('デモ用調査データの作成が完了しました')
            )
            self.stdout.write(
                f'チェックリストURL: /surveys/{survey.id}/checklist/cross-replacement/'
            )
        else:
            self.stdout.write(
                self.style.WARNING('調査データは既に存在します')
            )
            self.stdout.write(
                f'既存チェックリストURL: /surveys/{survey.id}/checklist/cross-replacement/'
            )