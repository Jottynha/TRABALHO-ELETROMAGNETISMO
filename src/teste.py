import subprocess
import time

# Função para testar a execução do simulador
def testar_simulador():
    try:
        # Executa o simulador e espera o término (timeout de 10 minutos por exemplo)
        subprocess.run(['python3', 'src/main.py'], check=True, timeout=600)
        return True
    except subprocess.CalledProcessError:
        # Caso o simulador falhe
        return False
    except subprocess.TimeoutExpired:
        # Caso o simulador ultrapasse o tempo limite
        return False

# Rodar o simulador 20 vezes
sucessos = 0
total_testes = 20

for i in range(total_testes):
    print(f"Testando execução {i+1}...")
    if testar_simulador():
        sucessos += 1
    else:
        print(f"Falha na execução {i+1}")

# Calcular a probabilidade de sucesso
probabilidade = sucessos / total_testes
print(f"Probabilidade de sucesso: {probabilidade:.2f}")
