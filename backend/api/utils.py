def preprocess_spectacular_hook(result, generator, request, public):
    """
    Hook para preprocessar o schema do Spectacular
    Remove a necessidade de URLs absolutas
    """
    # Garantir que as URLs sejam relativas ao servidor atual
    if 'servers' in result:
        # Manter apenas o servidor local para desenvolvimento
        if hasattr(request, 'get_host'):
            result['servers'] = [
                {
                    'url': f"http://{request.get_host()}",
                    'description': 'Servidor Atual'
                }
            ]
    
    return result

def filter_endpoints_by_tags(result, generator, request, public):
    """
    Hook para filtrar endpoints e manter apenas os com tags definidas
    """
    # Tags permitidas
    allowed_tags = {'Autenticação', 'Usuários', 'Controle de Acesso', 'Utilitários'}
    
    if 'paths' in result:
        filtered_paths = {}
        
        for path, path_item in result['paths'].items():
            filtered_operations = {}
            
            for method, operation in path_item.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                    # Verificar se tem tags permitidas
                    operation_tags = operation.get('tags', [])
                    
                    # Se tem tag permitida, manter
                    if any(tag in allowed_tags for tag in operation_tags):
                        filtered_operations[method] = operation
            
            # Se tem operações válidas, manter o path
            if filtered_operations:
                filtered_paths[path] = filtered_operations
        
        result['paths'] = filtered_paths
    
    return result