from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.clickjacking import xframe_options_exempt


class URLMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """书写拦截器 拦截非登录状态下的非法访问"""
        # 定义允许非登录状态下访问的地址
        allow_urls = ['login/', 'login_account/', 'registry/', 'registry_account/', '/unique_username/', 'captcha/']
        # 拿到你的访问地址
        access_url = request.path[1:]

        if access_url not in allow_urls:
            user = request.session.get('user')
            if not user:
                return redirect('system:login')






