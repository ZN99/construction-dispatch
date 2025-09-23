from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from surveys.models import Surveyor


class LandingView(TemplateView):
    """システム選択ランディングページ"""
    template_name = 'order_management/landing.html'

    def get(self, request):
        # 既にログイン済みの場合は適切なシステムにリダイレクト
        if request.user.is_authenticated:
            # 現場調査員プロファイルがある場合
            try:
                surveyor = Surveyor.objects.get(user=request.user, is_active=True)
                return redirect('surveys:field_dashboard')
            except Surveyor.DoesNotExist:
                # 本部スタッフの場合
                if request.user.is_staff:
                    return redirect('order_management:dashboard')
                else:
                    # 権限が不明な場合はログアウト
                    from django.contrib.auth import logout
                    logout(request)

        return render(request, self.template_name)