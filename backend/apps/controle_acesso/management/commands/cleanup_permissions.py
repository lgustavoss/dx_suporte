from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from controle_acesso.models import PermissaoCustomizada
from collections import defaultdict

class Command(BaseCommand):
    help = 'Limpar permissões órfãs, inativas e duplicadas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--remove-inactive',
            action='store_true',
            help='Remover permissões customizadas inativas',
        )
        parser.add_argument(
            '--remove-orphaned',
            action='store_true',
            help='Remover permissões Django sem correspondente customizada',
        )
        parser.add_argument(
            '--remove-duplicates',
            action='store_true',
            help='Remover permissões Django duplicadas',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Executar todas as operações de limpeza',
        )

    def handle(self, *args, **options):
        if options['all']:
            options['remove_inactive'] = True
            options['remove_orphaned'] = True
            options['remove_duplicates'] = True
        
        total_removed = 0
        
        if options['remove_duplicates']:
            self.stdout.write("🔍 Procurando permissões duplicadas...")
            removed = self.remove_duplicates()
            total_removed += removed
        
        if options['remove_inactive']:
            self.stdout.write("🔍 Removendo permissões inativas...")
            inactive_count = PermissaoCustomizada.objects.filter(ativo=False).count()
            PermissaoCustomizada.objects.filter(ativo=False).delete()
            self.stdout.write(f"🗑️  {inactive_count} permissões inativas removidas")
            total_removed += inactive_count
        
        if options['remove_orphaned']:
            self.stdout.write("🔍 Removendo permissões órfãs...")
            # Encontrar permissões Django sem correspondente customizada
            custom_codenames = PermissaoCustomizada.objects.values_list('nome', flat=True)
            orphaned = Permission.objects.exclude(codename__in=custom_codenames)
            
            # Filtrar apenas permissões que parecem ser nossas
            our_orphaned = orphaned.filter(codename__contains='_')
            count = our_orphaned.count()
            
            if count > 0:
                our_orphaned.delete()
                self.stdout.write(f"🗑️  {count} permissões Django órfãs removidas")
                total_removed += count
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Limpeza concluída! {total_removed} permissões removidas no total.')
        )
    
    def remove_duplicates(self):
        """Remover permissões Django duplicadas"""
        # Encontrar duplicatas
        duplicates = defaultdict(list)
        
        for perm in Permission.objects.all():
            key = perm.codename
            duplicates[key].append(perm)
        
        cleaned = 0
        for codename, perms in duplicates.items():
            if len(perms) > 1:
                self.stdout.write(f"\n🔍 Duplicata encontrada: {codename}")
                for perm in perms:
                    self.stdout.write(f"  - ID: {perm.id}, App: {perm.content_type.app_label}, Model: {perm.content_type.model}")
                
                # Manter apenas a primeira (mais antiga)
                to_keep = perms[0]
                to_delete = perms[1:]
                
                for perm in to_delete:
                    self.stdout.write(f"  ❌ Deletando: ID {perm.id} ({perm.content_type.app_label})")
                    perm.delete()
                    cleaned += 1
        
        self.stdout.write(f"\n✅ {cleaned} permissões duplicadas removidas!")
        return cleaned