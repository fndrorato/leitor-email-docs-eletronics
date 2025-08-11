from django.urls import path
from emissores.views import EmissorListView


urlpatterns = [
    path('emissores/', EmissorListView.as_view(), name='emissor-list'),
]
