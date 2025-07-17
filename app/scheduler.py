import threading
import time

class Scheduler:
    def __init__(self, callback, intervalo_minutos=60):
        self.callback = callback
        self.intervalo = intervalo_minutos * 60  # segundos
        self.thread = None
        self.running = False
        self.contagem_callback = None  # função para atualizar o contador na interface

    def iniciar(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._executar_loop, daemon=True)
            self.thread.start()

    def _executar_loop(self):
        while self.running:
            for i in range(self.intervalo, 0, -1):
                if not self.running:
                    return  # Encerra imediatamente se parar

                if self.contagem_callback:
                    mins, secs = divmod(i, 60)
                    tempo_formatado = f"{mins:02d}:{secs:02d}"
                    self.contagem_callback(tempo_formatado)

                time.sleep(1)

            if self.running:
                try:
                    self.callback()
                except Exception as e:
                    print(f"[Scheduler] Erro ao executar callback: {e}")

    def parar(self):
        self.running = False

    def atualizar_intervalo(self, novo_min):
        self.intervalo = novo_min * 60

    def set_contagem_callback(self, func):
        self.contagem_callback = func
