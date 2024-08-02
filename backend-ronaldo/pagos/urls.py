from django.urls import path
from pagos import views


urlpatterns = [
    path('stripe-usuario/', views.StripeUsuario.as_view(), name='stripe-usuarios'),
    path('stripe-chofer/', views.StripeChofer.as_view(), name='stripe-chofer'),
    path('chofer/<uuid:id>', views.Chofer.as_view(), name='chofer'),
    path('stripe-webhooks/', views.Webhooks.as_view(), name='webhooks'),
    path('balance/<uuid:id>/', views.Wallet.as_view(), name='balance'),
    path('pagos/', views.Pagos.as_view(), name='pagos'),
    path('transferencias/', views.Transferencias.as_view(), name='transferencias'),
    path('transferencia/<uuid:id>', views.Transferencia.as_view(), name='transferencia'),
    path('obtener-contactos/<uuid:id>', views.ObtenerContactos.as_view(), name='contactos'),
    # path('validar-imagen/<uuid:id>/', views.ValidarImagenes.as_view(), name='validar-imagen'),
]
