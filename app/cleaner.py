import os
import shutil

def limpar_pasta(caminho, progresso_callback=None):
    if not os.path.exists(caminho):
        return False, f"Pasta não encontrada: {caminho}"

    arquivos_encontrados = []
    pastas_encontradas = []

    for root, dirs, files in os.walk(caminho, topdown=False):
        for f in files:
            arquivos_encontrados.append(os.path.join(root, f))
        for d in dirs:
            pastas_encontradas.append(os.path.join(root, d))

    total = len(arquivos_encontrados) + len(pastas_encontradas)
    if total == 0:
        return True, f"Nenhum arquivo ou pasta para limpar em: {caminho}"

    i = 0

    for path in arquivos_encontrados:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Erro ao remover arquivo {path}: {e}")
        i += 1
        if progresso_callback:
            progresso_callback(int((i / total) * 100))

    for path in pastas_encontradas:
        try:
            shutil.rmtree(path, ignore_errors=True)
        except Exception as e:
            print(f"Erro ao remover pasta {path}: {e}")
        i += 1
        if progresso_callback:
            progresso_callback(int((i / total) * 100))

    return True, f"Limpeza realizada em: {caminho}"
