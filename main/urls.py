from django.urls import path

from main.views import ReportView, MiceData, create_group_view

urlpatterns = [
    path('report/', ReportView.as_view(), name='report'),
    path('mice_data/', MiceData.as_view(), name='mice_data'),
    path('create_group/', create_group_view, name='create_group')
]