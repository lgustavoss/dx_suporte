from django.core.management.base import BaseCommand
from controle_acesso.models import PermissaoCustomizada, GrupoCustomizado
from django.contrib.auth.models import Group
from accounts.models import Usuario

class Command(BaseCommand):
    help = 'Resetar dados de teste e sincronizar permissões'

    def handle(self, *args, **options):
        self.stdout.write("🧹 Limpando dados de teste...")
        
        # Remover usuários de teste
        test_users = Usuario.objects.filter(
            username__startswith='test_'
        )
        count = test_users.count()
        test_users.delete()
        self.stdout.write(f"🗑️  {count} usuários de teste removidos")
        
        # Remover grupos de teste
        test_groups = Group.objects.filter(
            name__icontains='test'
        )
        count = test_groups.count()
        test_groups.delete()
        self.stdout.write(f"🗑️  {count} grupos de teste removidos")
        
        # Sincronizar permissões
        from controle_acesso.utils import sync_permissions
        created = sync_permissions()
        self.stdout.write(f"🔄 {created} permissões sincronizadas")
        
        self.stdout.write(
            self.style.SUCCESS('✅ Reset concluído!')
        )