from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from controle_acesso.models import PermissaoCustomizada, GrupoCustomizado

class Command(BaseCommand):
    help = 'Configurar permissões para testes'

    def handle(self, *args, **options):
        # Criar permissões de controle_acesso
        content_type = ContentType.objects.get_for_model(GrupoCustomizado)
        
        permissions_data = [
            ('controle_acesso_gerenciar', 'Gerenciar controle de acesso'),
            ('controle_acesso_visualizar', 'Visualizar controle de acesso'),
            ('controle_acesso_criar', 'Criar controle de acesso'),
            ('controle_acesso_editar', 'Editar controle de acesso'),
            ('controle_acesso_excluir', 'Excluir controle de acesso'),
        ]
        
        created = 0
        for codename, name in permissions_data:
            # Criar permissão customizada
            perm_custom, created_custom = PermissaoCustomizada.objects.get_or_create(
                nome=codename,
                defaults={
                    'modulo': 'controle_acesso',
                    'acao': codename.split('_')[1],
                    'descricao': name,
                    'ativo': True
                }
            )
            
            # Criar permissão Django
            perm_django, created_django = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            
            if created_custom or created_django:
                created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {created} permissões configuradas para testes!')
        )