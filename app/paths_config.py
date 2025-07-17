import os
import json

def caminho_config():
    base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
    pasta_config = os.path.join(base, "AutoCleaner")
    os.makedirs(pasta_config, exist_ok=True)
    return os.path.join(pasta_config, "user_paths.json")

def carregar_pastas():
    try:
        with open(caminho_config(), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"[ERRO] Falha ao carregar JSON: {e}")
        return []

def salvar_pastas(pastas):
    try:
        with open(caminho_config(), "w", encoding="utf-8") as f:
            json.dump(pastas, f, indent=4)
    except Exception as e:
        print(f"[ERRO] Falha ao salvar JSON: {e}")

def adicionar_pasta(nova_pasta):
    pastas = carregar_pastas()
    if nova_pasta not in pastas:
        pastas.append(nova_pasta)
        salvar_pastas(pastas)

def remover_pasta(pasta):
    pastas = carregar_pastas()
    if pasta in pastas:
        pastas.remove(pasta)
        salvar_pastas(pastas)
