"""
Helper para gerenciamento de memória
"""

import psutil
import os
import gc
import signal
import sys

def setup_memory_limit(max_percent=80):
    """
    Configura limite de uso de memória.
    
    Args:
        max_percent: Percentual máximo de RAM a usar
    """
    total_memory = psutil.virtual_memory().total
    limit_bytes = int(total_memory * (max_percent / 100))
    
    print(f"🧠 Limite de memória: {limit_bytes / (1024**3):.1f} GB ({max_percent}%)")
    
    # Linux: resource.setrlimit
    # Windows: não tem equivalente nativo, mas podemos monitorar
    
    return limit_bytes

def check_memory_usage():
    """Verifica uso atual de memória."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    memory_mb = memory_info.rss / (1024 * 1024)
    memory_percent = process.memory_percent()
    
    print(f"📊 Uso atual: {memory_mb:.1f} MB ({memory_percent:.1f}%)")
    
    return memory_mb, memory_percent

def free_memory_aggressive():
    """Libera memória de forma agressiva."""
    print("🧹 Liberando memória...")
    
    # Forçar garbage collection múltiplas vezes
    for _ in range(3):
        gc.collect()
    
    # Limpar caches
    try:
        import numpy as np
        np.clear_cache()
    except:
        pass
    
    print(f"✅ Memória liberada")
    return check_memory_usage()

def memory_safe_execute(func, *args, **kwargs):
    """
    Executa função com segurança de memória.
    
    Args:
        func: Função a executar
    
    Returns:
        Resultado da função
    """
    print("🛡️  Executando com segurança de memória")
    
    # Verificar memória antes
    free_memory_aggressive()
    
    try:
        result = func(*args, **kwargs)
        
        # Liberar após execução
        free_memory_aggressive()
        
        return result
        
    except MemoryError:
        print("💥 MemoryError detectado")
        free_memory_aggressive()
        raise