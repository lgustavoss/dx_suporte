from django.db.models import Q
from rest_framework import filters
from django_filters import rest_framework as django_filters

class GlobalSearchFilter(filters.SearchFilter):
    """Filtro de busca global que procura em múltiplas colunas"""
    
    def filter_queryset(self, request, queryset, view):
        search_param = self.get_search_terms(request)
        
        if not search_param:
            return queryset
        
        search_term = ' '.join(search_param)
        
        # Campos de busca definidos na view
        search_fields = getattr(view, 'search_fields', [])
        
        if not search_fields:
            return queryset
        
        # Construir query OR para buscar em todas as colunas
        search_queries = Q()
        
        for field in search_fields:
            # Remove prefixos do DRF (^, =, @, $)
            clean_field = field.lstrip('^=@$')
            
            # Adicionar busca case-insensitive
            search_queries |= Q(**{f"{clean_field}__icontains": search_term})
        
        return queryset.filter(search_queries).distinct()

class UsuarioFilter(django_filters.FilterSet):
    """Filtros específicos para usuários"""
    is_online = django_filters.BooleanFilter(field_name='is_online')
    is_active = django_filters.BooleanFilter(field_name='is_active')
    created_after = django_filters.DateFilter(field_name='date_joined', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='date_joined', lookup_expr='lte')
    
    class Meta:
        model = None  # Será definido na view
        fields = ['is_online', 'is_active', 'created_after', 'created_before']

class GrupoFilter(django_filters.FilterSet):
    """Filtros específicos para grupos"""
    ativo = django_filters.BooleanFilter(field_name='ativo')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    nome = django_filters.CharFilter(field_name='group__name', lookup_expr='icontains')  # ← NOVO
    
    class Meta:
        model = None  # Será definido na view
        fields = ['ativo', 'created_after', 'created_before', 'nome']