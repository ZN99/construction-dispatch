from datetime import timedelta
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import Craftsman, Assignment, CraftsmanSchedule, Project


class CraftsmanMatcher:
    """職人マッチングロジック"""

    def __init__(self):
        self.weights = {
            "availability": 40,  # 空き時間
            "skill_match": 30,  # 技能マッチ
            "location": 20,  # 地域近接
            "cost": 10,  # コスト
        }

    def find_best_matches(self, project, start_date, end_date, limit=10):
        """
        プロジェクトに最適な職人を検索

        優先順位: 空き時間 > 技能マッチ > 地域近接 > コスト安
        """
        # 基本フィルタリング
        available_craftsmen = self._get_available_craftsmen(
            project.project_type, start_date, end_date
        )

        # スコア計算
        scored_craftsmen = []
        for craftsman in available_craftsmen:
            score = self._calculate_match_score(
                craftsman, project, start_date, end_date
            )
            scored_craftsmen.append(
                {
                    "craftsman": craftsman,
                    "score": score,
                    "availability_score": score["availability"],
                    "skill_score": score["skill_match"],
                    "location_score": score["location"],
                    "cost_score": score["cost"],
                    "total_score": score["total"],
                }
            )

        # スコア順でソート
        scored_craftsmen.sort(key=lambda x: x["total_score"], reverse=True)

        return scored_craftsmen[:limit]

    def _get_available_craftsmen(self, project_type, start_date, end_date):
        """基本的なフィルタリングで利用可能な職人を取得"""
        return (
            Craftsman.objects.filter(is_active=True, specialties=project_type)
            .prefetch_related("specialties", "craftsmanschedule_set", "assignment_set")
            .distinct()
        )

    def _calculate_match_score(self, craftsman, project, start_date, end_date):
        """マッチングスコアを計算"""
        scores = {}

        # 1. 空き時間スコア (40%)
        scores["availability"] = self._calculate_availability_score(
            craftsman, start_date, end_date
        )

        # 2. 技能マッチスコア (30%)
        scores["skill_match"] = self._calculate_skill_score(craftsman, project)

        # 3. 地域近接スコア (20%)
        scores["location"] = self._calculate_location_score(craftsman, project)

        # 4. コストスコア (10%)
        scores["cost"] = self._calculate_cost_score(craftsman)

        # 総合スコア計算
        scores["total"] = (
            scores["availability"] * self.weights["availability"]
            + scores["skill_match"] * self.weights["skill_match"]
            + scores["location"] * self.weights["location"]
            + scores["cost"] * self.weights["cost"]
        ) / 100

        return scores

    def _calculate_availability_score(self, craftsman, start_date, end_date):
        """空き時間スコア計算"""
        # 指定期間中の稼働可能日数を計算
        total_days = (end_date - start_date).days + 1
        available_days = 0

        current_date = start_date
        while current_date <= end_date:
            if craftsman.can_work_on(current_date):
                available_days += 1
            current_date += timedelta(days=1)

        if total_days == 0:
            return 0

        # 空き時間の割合をスコアに変換 (0-100)
        availability_ratio = available_days / total_days
        return availability_ratio * 100

    def _calculate_skill_score(self, craftsman, project):
        """技能マッチスコア計算"""
        base_score = 50  # 基本スコア

        # 工種マッチ
        if project.project_type in craftsman.specialties.all():
            base_score += 30

        # スキルレベルボーナス
        skill_bonus = (craftsman.skill_level - 1) * 5  # レベル1=0, レベル5=20

        # 評価ボーナス
        rating_bonus = float(craftsman.average_rating) * 4  # 最大5.0 * 4 = 20

        return min(base_score + skill_bonus + rating_bonus, 100)

    def _calculate_location_score(self, craftsman, project):
        """地域近接スコア計算"""
        # 簡易的な地域マッチング
        if not craftsman.coverage_areas or not project.address:
            return 50  # 中立スコア

        project_areas = self._extract_area_keywords(project.address)
        craftsman_areas = craftsman.coverage_area_list

        # エリアマッチング
        matches = 0
        for project_area in project_areas:
            for craftsman_area in craftsman_areas:
                if project_area in craftsman_area or craftsman_area in project_area:
                    matches += 1
                    break

        if not project_areas:
            return 50

        match_ratio = matches / len(project_areas)
        return match_ratio * 100

    def _calculate_cost_score(self, craftsman):
        """コストスコア計算（安いほど高スコア）"""
        # 時給の逆数を使用（最大時給を設定してスケール調整）
        max_rate = 8000  # 最大時給の想定
        min_rate = 1000  # 最小時給の想定

        if craftsman.hourly_rate <= min_rate:
            return 100
        elif craftsman.hourly_rate >= max_rate:
            return 0
        else:
            # 線形逆変換
            normalized_rate = (float(craftsman.hourly_rate) - min_rate) / (
                max_rate - min_rate
            )
            return (1 - normalized_rate) * 100

    def _extract_area_keywords(self, address):
        """住所からエリアキーワードを抽出"""
        import re

        # 都道府県・市区町村を抽出
        patterns = [
            r"([東京都|大阪府|京都府|北海道|.*県])",
            r"([^都道府県]*[市区町村])",
            r"([^市区町村]*区)",
        ]

        areas = []
        for pattern in patterns:
            matches = re.findall(pattern, address)
            areas.extend(matches)

        return list(set(areas))  # 重複除去

    def get_workload_analysis(self, craftsman, days=30):
        """職人の稼働率分析"""
        from django.utils import timezone

        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days)

        # 期間中のアサイン状況
        assignments = Assignment.objects.filter(
            craftsman=craftsman,
            status__in=["confirmed", "in_progress"],
            scheduled_start_date__lte=end_date,
            scheduled_end_date__gte=start_date,
        )

        busy_days = 0
        current_date = start_date

        while current_date <= end_date:
            # その日にアサインがあるかチェック
            day_assignments = assignments.filter(
                scheduled_start_date__lte=current_date,
                scheduled_end_date__gte=current_date,
            )

            if day_assignments.exists():
                busy_days += 1

            current_date += timedelta(days=1)

        workload_percentage = (busy_days / days) * 100

        return {
            "total_days": days,
            "busy_days": busy_days,
            "available_days": days - busy_days,
            "workload_percentage": workload_percentage,
            "status": self._get_workload_status(workload_percentage),
        }

    def _get_workload_status(self, percentage):
        """稼働率から状態を判定"""
        if percentage >= 90:
            return {"level": "very_busy", "label": "非常に忙しい", "color": "danger"}
        elif percentage >= 70:
            return {"level": "busy", "label": "忙しい", "color": "warning"}
        elif percentage >= 40:
            return {"level": "moderate", "label": "適度", "color": "info"}
        else:
            return {"level": "available", "label": "余裕あり", "color": "success"}

    def suggest_alternative_dates(
        self, craftsman, preferred_start, preferred_end, project_type
    ):
        """代替日程を提案"""
        suggestions = []

        # 前後2週間で空いている期間を検索
        search_start = preferred_start - timedelta(days=14)
        search_end = preferred_end + timedelta(days=14)

        current_date = search_start
        while current_date <= search_end:
            # 必要な日数分連続で空いているかチェック
            required_days = (preferred_end - preferred_start).days + 1

            if self._check_consecutive_availability(
                craftsman, current_date, required_days
            ):
                suggestion_end = current_date + timedelta(days=required_days - 1)

                suggestions.append(
                    {
                        "start_date": current_date,
                        "end_date": suggestion_end,
                        "days_diff": abs((current_date - preferred_start).days),
                        "is_earlier": current_date < preferred_start,
                    }
                )

            current_date += timedelta(days=1)

        # 希望日に近い順でソート
        suggestions.sort(key=lambda x: x["days_diff"])

        return suggestions[:5]  # 上位5つの提案

    def _check_consecutive_availability(self, craftsman, start_date, required_days):
        """連続稼働可能日数をチェック"""
        for i in range(required_days):
            check_date = start_date + timedelta(days=i)
            if not craftsman.can_work_on(check_date):
                return False
        return True


# 職人検索用のユーティリティ関数
def search_craftsmen(filters):
    """フィルタ条件で職人を検索"""
    queryset = Craftsman.objects.filter(is_active=True)

    # 工種フィルタ
    if filters.get("project_type"):
        queryset = queryset.filter(specialties=filters["project_type"])

    # スキルレベルフィルタ
    if filters.get("skill_level"):
        queryset = queryset.filter(skill_level__gte=filters["skill_level"])

    # エリアフィルタ
    if filters.get("area"):
        queryset = queryset.filter(coverage_areas__icontains=filters["area"])

    # 時給範囲フィルタ
    if filters.get("max_hourly_rate"):
        queryset = queryset.filter(hourly_rate__lte=filters["max_hourly_rate"])

    # 評価フィルタ
    if filters.get("min_rating"):
        queryset = queryset.filter(average_rating__gte=filters["min_rating"])

    return queryset.select_related().prefetch_related("specialties")


def get_craftsman_availability_calendar(craftsman, start_date, end_date):
    """職人のカレンダー形式稼働状況を取得"""
    calendar_data = []
    current_date = start_date

    while current_date <= end_date:
        # その日のスケジュール情報を取得
        schedule = CraftsmanSchedule.objects.filter(
            craftsman=craftsman, date=current_date
        ).first()

        # アサイン情報を取得
        assignment = Assignment.objects.filter(
            craftsman=craftsman,
            status__in=["confirmed", "in_progress"],
            scheduled_start_date__lte=current_date,
            scheduled_end_date__gte=current_date,
        ).first()

        day_data = {
            "date": current_date,
            "is_available": schedule.is_available if schedule else True,
            "assignment": assignment,
            "status": "available",
        }

        # ステータス判定
        if assignment:
            day_data["status"] = "assigned"
        elif schedule and not schedule.is_available:
            day_data["status"] = "unavailable"

        calendar_data.append(day_data)
        current_date += timedelta(days=1)

    return calendar_data
