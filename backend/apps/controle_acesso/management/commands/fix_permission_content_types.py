from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.controle_acesso.models import PermissaoCustomizada

class Command(BaseCommand):
    help = 'Corrigir content_types das permissões Django'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Corrigindo content_types das permissões...")
        
        fixed_count = 0
        
        # ✅ CORREÇÃO: Importar modelos e usar classes
        from apps.accounts.models import Usuario
        
        # Mapear módulos para content_types corretos
        content_type_map = {
            'accounts': ContentType.objects.get_for_model(Usuario),
            'controle_acesso': ContentType.objects.get_for_model(PermissaoCustomizada),
        }
        
        # Obter todas as permissões customizadas
        for perm_custom in PermissaoCustomizada.objects.all():
            try:
                # Encontrar permissão Django correspondente
                django_perm = Permission.objects.get(codename=perm_custom.nome)
                
                # Determinar content_type correto
                correct_content_type = content_type_map.get(perm_custom.modulo)
                
                if correct_content_type and django_perm.content_type != correct_content_type:
                    old_ct = django_perm.content_type
                    django_perm.content_type = correct_content_type
                    django_perm.save()
                    
                    fixed_count += 1
                    self.stdout.write(
                        f"✅ {perm_custom.nome}: {old_ct.app_label}.{old_ct.model} → {correct_content_type.app_label}.{correct_content_type.model}"
                    )
                else:
                    # Para debug: mostrar permissões que já estão corretas
                    if correct_content_type:
                        self.stdout.write(f"✓ {perm_custom.nome}: já correto ({django_perm.content_type.app_label}.{django_perm.content_type.model})")
                    else:
                        self.stdout.write(f"⚠️ Módulo não mapeado: {perm_custom.modulo}")
                
            except Permission.DoesNotExist:
                self.stdout.write(f"⚠️ Permissão Django não encontrada: {perm_custom.nome}")
            except Exception as e:
                self.stdout.write(f"❌ Erro ao processar {perm_custom.nome}: {e}")
        
        self.stdout.write(
            self.style.SUCCESS(f"🎉 {fixed_count} permissões corrigidas!")
        )