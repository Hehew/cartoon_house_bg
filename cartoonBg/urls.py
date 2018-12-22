from django.urls import path, include
import cartoonBg.views as views

urlpatterns = [
    path('current_week/', views.index),
    path('only_me/', views.index),
    path('search_for_keyword/', views.search_for_keyword),
    path('hot_list/', views.index),
    path('get_info/', views.get_info),
    path('get_page_detail/', views.get_page_detail),
]