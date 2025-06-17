from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    """Paginação customizada para o sistema"""
    page_size = 10  # Registros por página (padrão)
    page_size_query_param = 'page_size'  # Permite alterar via parâmetro
    max_page_size = 100  # Máximo de registros por página
    
    def get_paginated_response(self, data):
        """Resposta customizada com mais informações"""
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })