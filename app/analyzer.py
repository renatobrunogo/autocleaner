import os

class TempAnalyzer:
    def __init__(self, pastas=None):
        self.paths = {}
        pastas_customizadas = pastas if pastas is not None else []
        for i, pasta in enumerate(pastas_customizadas, start=1):
            nome_chave = f"Pasta Personalizada #{i}"
            self.paths[nome_chave] = pasta

    def analyze(self, progresso_callback=None):
        resultados = {}
        for nome, caminho in self.paths.items():
            if os.path.exists(caminho):
                total_arquivos, total_tamanho = self._analisar_pasta(caminho, progresso_callback)
                resultados[nome] = (total_arquivos, total_tamanho)
        return resultados

    def _analisar_pasta(self, pasta, progresso_callback=None):
        total_arquivos = 0
        total_tamanho = 0
        arquivos_encontrados = []

        for root, _, files in os.walk(pasta):
            for f in files:
                try:
                    file_path = os.path.join(root, f)
                    arquivos_encontrados.append(file_path)
                except Exception:
                    pass

        total_itens = len(arquivos_encontrados)
        for i, file_path in enumerate(arquivos_encontrados, 1):
            try:
                total_arquivos += 1
                total_tamanho += os.path.getsize(file_path)
            except Exception:
                pass

            if progresso_callback and total_itens > 0:
                progresso = int((i / total_itens) * 100)
                progresso_callback(progresso)

        return total_arquivos, total_tamanho

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
