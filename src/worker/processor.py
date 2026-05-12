import time
import json
import sys
from datetime import datetime
from src.api.dependencies import queue


def process_task(task: dict):
    """Processa uma tarefa"""
    print(f"\n[{datetime.utcnow().isoformat()}] Tarefa:")
    print(json.dumps(task, indent=2, default=str))
    
    action = task.get("action", "unknown")
    
    if action == "GerarRelatorio":
        print("  ✓ Relatório gerado")
        time.sleep(1)
    elif action == "EnviarEmail":
        print("  ✓ Email enviado")
        time.sleep(0.5)
    else:
        print(f"  ✓ {action} concluída")
        time.sleep(0.3)
    
    print(f"  Concluído")


def run():
    """Loop principal do worker"""
    print(f"\n{'='*50}")
    print("Worker iniciado - Aguardando tarefas...")
    print(f"{'='*50}\n")
    
    try:
        while True:
            task = queue.pop_blocking(timeout=5)
            if task:
                process_task(task)
            else:
                print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\n\nWorker interrompido")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
