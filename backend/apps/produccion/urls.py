from django.urls import path
from . import views

urlpatterns = [
    path('ordenes/', views.OrdenListCreateView.as_view(), name='orden-list-create'),
    path('ordenes/<int:pk>/', views.OrdenDetailView.as_view(), name='orden-detail'),
    path('ventanas/<uuid:identificador>/historial/', views.VentanaHistorialView.as_view(), name='ventana-historial'),
    path('ventanas/<uuid:identificador>/avanzar/', views.VentanaAvanzarView.as_view(), name='ventana-avanzar'),
    path('ventanas/<uuid:identificador>/qr/', views.VentanaQRView.as_view(), name='ventana-qr'),
    path('dashboard/resumen/', views.DashboardResumenView.as_view(), name='dashboard-resumen'),
]
