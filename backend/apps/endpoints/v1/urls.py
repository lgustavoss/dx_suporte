from django.urls import path, include

urlpatterns = [
    # Autenticação
    path('auth/', include('accounts.urls')),

    # Controle de acesso
    path('controle-acesso/', include('controle_acesso.urls')),
    
    # Futuros endpoints
    # path('usuarios/', include('usuarios.urls')),
    # path('clientes/', include('clientes.urls')),
]