from django.core.management.base import BaseCommand
from surveys.models import SurveyWorkflowStep


class Command(BaseCommand):
    help = 'クロス張り替え調査用のワークフローステップを作成'

    def handle(self, *args, **options):
        steps_data = [
            {
                'step_number': 1,
                'step_type': 'room_setup',
                'title': '部屋の準備',
                'description': '調査環境の準備と安全確認',
                'instruction_html': '''
                <div class="instruction-details">
                    <h5>準備事項:</h5>
                    <ul>
                        <li>部屋の明かりをつけて、十分な明るさを確保</li>
                        <li>大きな家具は可能な限り壁から離す</li>
                        <li>メジャーとカメラを準備</li>
                        <li>安全に作業できる環境を整える</li>
                    </ul>
                    <p><strong>注意:</strong> 電気設備や危険物がないか確認してください。</p>
                </div>
                ''',
                'required_photos': 1,
                'estimated_minutes': 10,
                'is_mandatory': True
            },
            {
                'step_number': 2,
                'step_type': 'wall_measurement',
                'title': '壁面の測定',
                'description': '壁面のサイズを正確に測定',
                'instruction_html': '''
                <div class="measurement-guide">
                    <h5>測定手順:</h5>
                    <ol>
                        <li>メジャーを壁の端から端まで当てる</li>
                        <li>横幅（左右の長さ）を測定</li>
                        <li>高さ（床から天井まで）を測定</li>
                        <li>ドアや窓などの開口部面積を計算</li>
                    </ol>
                    <p><strong>注意:</strong> cm単位で正確に測定してください。</p>
                </div>
                ''',
                'required_photos': 1,
                'estimated_minutes': 15,
                'is_mandatory': True
            },
            {
                'step_number': 3,
                'step_type': 'condition_check',
                'title': '下地状態の確認',
                'description': '壁面の下地材質と状態をチェック',
                'instruction_html': '''
                <div class="condition-guide">
                    <h5>確認項目:</h5>
                    <ul>
                        <li><strong>下地材質:</strong> 石膏ボード、コンクリート、合板、その他</li>
                        <li><strong>下地状態:</strong> 良好、補修必要</li>
                        <li><strong>表面状態:</strong> 平滑性、ひび割れ、凹み</li>
                    </ul>
                    <p><strong>判断基準:</strong> 軽く叩いて音で材質を判断し、目視で状態を確認。</p>
                </div>
                ''',
                'required_photos': 0,
                'estimated_minutes': 10,
                'is_mandatory': True
            },
            {
                'step_number': 4,
                'step_type': 'photo_capture',
                'title': '写真撮影',
                'description': '壁面状態の記録写真を撮影',
                'instruction_html': '''
                <div class="photo-guide">
                    <h5>撮影項目:</h5>
                    <ul>
                        <li><strong>壁面全体:</strong> クロスの状態がわかる全景</li>
                        <li><strong>損傷箇所:</strong> 傷、汚れ、剥がれなどの詳細</li>
                        <li><strong>特記事項:</strong> 気になる部分があれば追加撮影</li>
                    </ul>
                    <p><strong>撮影のコツ:</strong> 明るい場所で、ピントを合わせて鮮明に撮影。</p>
                </div>
                ''',
                'required_photos': 2,
                'estimated_minutes': 10,
                'is_mandatory': True
            },
            {
                'step_number': 5,
                'step_type': 'damage_assessment',
                'title': '損傷評価',
                'description': '現在のクロスの損傷状況を評価',
                'instruction_html': '''
                <div class="damage-guide">
                    <h5>評価項目:</h5>
                    <ul>
                        <li><strong>汚れ・変色:</strong> 程度と範囲</li>
                        <li><strong>破れ・剥がれ:</strong> 箇所数と大きさ</li>
                        <li><strong>釘穴・画鋲穴:</strong> 数と深さ</li>
                        <li><strong>その他:</strong> カビ、水染み、タバコヤニなど</li>
                    </ul>
                    <p><strong>評価基準:</strong> 軽微、普通、重度で分類してください。</p>
                </div>
                ''',
                'required_photos': 1,
                'estimated_minutes': 15,
                'is_mandatory': True
            },
            {
                'step_number': 6,
                'step_type': 'completion_check',
                'title': '完了確認',
                'description': '調査内容の最終確認',
                'instruction_html': '''
                <div class="completion-guide">
                    <h5>確認事項:</h5>
                    <ul>
                        <li>すべての測定値が記録されているか</li>
                        <li>必要な写真が撮影されているか</li>
                        <li>下地状態が正しく選択されているか</li>
                        <li>損傷評価が完了しているか</li>
                    </ul>
                    <p><strong>最終チェック:</strong> 不備がないか再度確認してください。</p>
                </div>
                ''',
                'required_photos': 0,
                'estimated_minutes': 5,
                'is_mandatory': True
            }
        ]

        created_count = 0
        for step_data in steps_data:
            step, created = SurveyWorkflowStep.objects.get_or_create(
                step_number=step_data['step_number'],
                defaults=step_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'ステップ {step.step_number}: {step.title} を作成しました')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'ステップ {step.step_number}: {step.title} は既に存在します')
                )

        self.stdout.write(
            self.style.SUCCESS(f'{created_count}個の新しいワークフローステップを作成しました。')
        )