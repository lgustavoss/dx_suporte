from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from controle_acesso.models import PermissaoCustomizada, GrupoCustomizado
from accounts.models import Usuario

class Command(BaseCommand):
    help = 'Gerar relatório detalhado do sistema de permissões'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📊 RELATÓRIO DO SISTEMA DE PERMISSÕES'))
        self.stdout.write('=' * 60)
        
        # 1. Estatísticas gerais
        total_custom = PermissaoCustomizada.objects.count()
        active_custom = PermissaoCustomizada.objects.filter(ativo=True).count()
        total_django = Permission.objects.count()
        
        self.stdout.write(f"\n📋 ESTATÍSTICAS GERAIS:")
        self.stdout.write(f"   • Permissões Customizadas: {active_custom}/{total_custom}")
        self.stdout.write(f"   • Permissões Django: {total_django}")
        
        # 2. Por módulo
        modules = PermissaoCustomizada.objects.values('modulo').distinct()
        self.stdout.write(f"\n🔍 POR MÓDULO:")
        for module in modules:
            mod_name = module['modulo']
            count = PermissaoCustomizada.objects.filter(
                modulo=mod_name, ativo=True
            ).count()
            self.stdout.write(f"   • {mod_name}: {count} permissões")
        
        # 3. Grupos e usuários
        total_groups = GrupoCustomizado.objects.count()
        total_users = Usuario.objects.filter(is_active=True).count()
        admin_users = Usuario.objects.filter(is_superuser=True, is_active=True).count()
        
        self.stdout.write(f"\n👥 USUÁRIOS E GRUPOS:")
        self.stdout.write(f"   • Grupos: {total_groups}")
        self.stdout.write(f"   • Usuários ativos: {total_users}")
        self.stdout.write(f"   • Administradores: {admin_users}")
        
        # 4. Permissões órfãs
        custom_codenames = set(PermissaoCustomizada.objects.values_list('nome', flat=True))
        django_codenames = set(Permission.objects.values_list('codename', flat=True))
        
        orphaned_django = django_codenames - custom_codenames
        orphaned_custom = custom_codenames - django_codenames
        
        self.stdout.write(f"\n⚠️  ANÁLISE DE INTEGRIDADE:")
        self.stdout.write(f"   • Permissões Django órfãs: {len(orphaned_django)}")
        self.stdout.write(f"   • Permissões Customizadas órfãs: {len(orphaned_custom)}")
        
        if orphaned_custom:
            self.stdout.write("   📝 Permissões customizadas sem Django correspondente:")
            for perm in list(orphaned_custom)[:5]:  # Mostrar apenas 5
                self.stdout.write(f"      - {perm}")