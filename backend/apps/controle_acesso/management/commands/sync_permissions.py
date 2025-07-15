from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from apps.controle_acesso.models import PermissaoCustomizada
from controle_acesso.utils import get_app_permissions
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sincronizar permissões customizadas com permissões Django'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostrar o que seria criado, sem executar',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar criação mesmo se já existir',
        )
        parser.add_argument(
            '--app',
            type=str,
            help='Sincronizar apenas um app específico',
        )

    def handle(self, *args, **options):
        """Executar sincronização de permissões"""
        try:
            self.stdout.write("🚀 Iniciando sincronização de permissões...")
            
            # Obter permissões dos apps
            app_permissions = get_app_permissions()
            self.stdout.write(f"📋 Encontradas {len(app_permissions)} permissões para processar")
            
            if options['dry_run']:
                self._simulate_sync(app_permissions)
                return
            
            # ✅ EXECUTAR SINCRONIZAÇÃO REAL
            created_custom = 0
            created_django = 0
            errors = 0
            
            with transaction.atomic():
                for perm_data in app_permissions:
                    try:
                        # ✅ 1. CRIAR/VERIFICAR PERMISSÃO CUSTOMIZADA
                        perm_custom, created = PermissaoCustomizada.objects.get_or_create(
                            nome=perm_data['nome'],
                            defaults={
                                'modulo': perm_data['modulo'],
                                'acao': perm_data['acao'],
                                'descricao': f"{perm_data['acao'].title()} {perm_data['modulo_display']}",
                                'auto_descoberta': True,
                                'ativo': True
                            }
                        )
                        
                        if created:
                            created_custom += 1
                            self.stdout.write(f"  ✅ Permissão customizada criada: {perm_custom.nome}")
                        
                        # ✅ 2. CRIAR/VERIFICAR PERMISSÃO DJANGO
                        try:
                            # Verificar se permissão Django já existe
                            django_perm = Permission.objects.get(codename=perm_custom.nome)
                            # self.stdout.write(f"  📋 Permissão Django já existe: {django_perm.codename}")
                        except Permission.DoesNotExist:
                            # Criar permissão Django
                            content_type = self._get_content_type_for_module(perm_custom.modulo)
                            
                            django_perm = Permission.objects.create(
                                codename=perm_custom.nome,
                                name=perm_custom.descricao or f"{perm_custom.acao} {perm_custom.modulo}",
                                content_type=content_type
                            )
                            created_django += 1
                            self.stdout.write(f"  ✅ Permissão Django criada: {django_perm.codename}")
                    
                    except Exception as e:
                        errors += 1
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Erro ao processar {perm_data['nome']}: {e}")
                        )
            
            # ✅ RESULTADO FINAL
            self.stdout.write(
                self.style.SUCCESS(f"""🎉 Sincronização concluída!
   • {created_custom} permissões customizadas criadas
   • {created_django} permissões Django criadas
   • {errors} erros encontrados""")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro durante sincronização: {e}")
            )

    def _get_content_type_for_module(self, module_name):
        """Determinar content_type baseado no módulo"""
        if module_name == 'accounts':
            from apps.accounts.models import Usuario
            return ContentType.objects.get_for_model(Usuario)
        elif module_name == 'controle_acesso':
            return ContentType.objects.get_for_model(PermissaoCustomizada)
        else:
            # Content type genérico para outros módulos
            from django.contrib.contenttypes.models import ContentType
            return ContentType.objects.get_for_model(ContentType)

    def _simulate_sync(self, app_permissions):
        """Simular sincronização para dry-run"""
        would_create_custom = 0
        would_create_django = 0
        
        for perm_data in app_permissions:
            # Verificar se permissão customizada existiria
            if not PermissaoCustomizada.objects.filter(nome=perm_data['nome']).exists():
                would_create_custom += 1
                self.stdout.write(f"  + Criaria permissão customizada: {perm_data['nome']}")
            
            # Verificar se permissão Django existiria
            if not Permission.objects.filter(codename=perm_data['nome']).exists():
                would_create_django += 1
                self.stdout.write(f"  + Criaria permissão Django: {perm_data['nome']}")
        
        self.stdout.write(f"🔍 Simulação concluída (DRY-RUN)")
        self.stdout.write(f"   • {len(app_permissions)} permissões seriam processadas")
        self.stdout.write(f"   • {would_create_custom} permissões customizadas seriam criadas")
        self.stdout.write(f"   • {would_create_django} permissões Django seriam criadas")
        self.stdout.write("   • Execute sem --dry-run para aplicar as alterações")