import tkinter as tk
import tkinter.ttk as ttk
import sys
import os
import threading
from tkinter import filedialog, messagebox
from analyzer import TempAnalyzer
from cleaner import limpar_pasta
from scheduler import Scheduler
from paths_config import carregar_pastas, adicionar_pasta, remover_pasta  # Usar funções do paths_config

def recurso_caminho(rel_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

def centralizar_janela(janela, largura, altura):
    tela_largura = janela.winfo_screenwidth()
    tela_altura = janela.winfo_screenheight()
    x = (tela_largura // 2) - (largura // 2)
    y = (tela_altura // 2) - (altura // 2)
    janela.geometry(f'{largura}x{altura}+{x}+{y}')

def analisar():
    texto_resultado.delete("1.0", tk.END)
    pastas = carregar_pastas()
    analisador = TempAnalyzer(pastas)

    total = len(pastas)
    if total == 0:
        texto_resultado.insert(tk.END, "Nenhuma pasta encontrada para analisar.\n")
        atualizar_progresso(0)
        return

    def progresso(percent):
        atualizar_progresso(percent)

    resultados = analisador.analyze(progresso_callback=progresso)

    for nome, (arquivos, tamanho) in resultados.items():
        caminho = analisador.paths[nome]
        nome_pasta = os.path.basename(caminho)
        tamanho_formatado = analisador.format_size(tamanho)
        texto_resultado.insert(tk.END, f"Pasta: {nome_pasta}\n → {arquivos} arquivos | {tamanho_formatado}\n\n")

    atualizar_progresso(100)

def limpar():
    confirm = messagebox.askyesno(
        "ATENÇÃO!", "⚠️ Esta ação é irreversível!\n\n"
        "Tem certeza que deseja limpar as pastas selecionadas?"
        )
    if not confirm:
        return

    texto_resultado.delete("1.0", tk.END)
    pastas = carregar_pastas()
    analisador = TempAnalyzer(pastas)
    resultados = analisador.analyze()

    total = len(resultados)
    if total == 0:
        texto_resultado.insert(tk.END, "Nenhuma pasta encontrada para limpar.\n")
        atualizar_progresso(0)
        return

    for nome, caminho in analisador.paths.items():
        def progresso(percent):
            atualizar_progresso(percent)
        sucesso, msg = limpar_pasta(caminho, progresso_callback=progresso)
        texto_resultado.insert(tk.END, f"[{'OK' if sucesso else 'ERRO'}] {msg}\n")

    messagebox.showinfo("Limpeza finalizada", "Todas as pastas foram limpas.")
    atualizar_progresso(100)

def limpeza_automatica():
    def callback_limpar(desativar_auto):
        def tarefa_limpeza():
            pastas = carregar_pastas()
            analisador = TempAnalyzer(pastas)
            resultados = analisador.analyze()
            logs = []

            if not resultados:
                logs.append("Nenhuma pasta encontrada para limpar.\n")
            else:
                for nome, caminho in analisador.paths.items():
                    sucesso, msg = limpar_pasta(caminho)
                    logs.append(f"[{'OK' if sucesso else 'ERRO'}] {msg}\n")

            def atualizar_interface():
                texto_resultado.delete("1.0", tk.END)
                texto_resultado.insert(tk.END, "".join(logs))
                messagebox.showinfo("AutoCleaner", "Limpeza automática executada!")

                if not desativar_auto:
                    scheduler.iniciar()
                else:
                    parar_scheduler()

            root.after(0, atualizar_interface)

        threading.Thread(target=tarefa_limpeza, daemon=True).start()

    def callback_cancelar(desativar_auto):
        if not desativar_auto:
            scheduler.iniciar()
        else:
            parar_scheduler()

    scheduler.parar()
    mostrar_confirmacao_limpeza_automatica(callback_limpar, callback_cancelar)

def mostrar_confirmacao_limpeza_automatica(callback_limpar, callback_cancelar):
    confirm_win = tk.Toplevel(root)
    confirm_win.title("Confirmar limpeza automática")
    confirm_win.configure(bg="#f5f5f5")
    confirm_win.grab_set()  # Bloqueia a janela principal
    confirm_win.iconbitmap(recurso_caminho("assets/autocleaner-off.ico"))

    centralizar_janela(confirm_win, 420, 200)

    label = tk.Label(confirm_win, text="Deseja executar a limpeza automática agora?",
                     bg="#f5f5f5", font=("Segoe UI", 10, "bold"))
    label.pack(pady=(20, 10))

    var_desativar = tk.BooleanVar()

    chk = tk.Checkbutton(confirm_win, text="Desativar limpeza automática após essa ação",
                         variable=var_desativar, bg="#f5f5f5")
    chk.pack(pady=5)

    def on_confirm():
        confirmar = True
        desativar = var_desativar.get()
        confirm_win.destroy()
        callback_limpar(desativar)

    def on_cancel():
        desativar = var_desativar.get()
        confirm_win.destroy()
        callback_cancelar(desativar)

    frame_botoes = tk.Frame(confirm_win, bg="#f5f5f5")
    frame_botoes.pack(pady=20)

    tk.Button(frame_botoes, text="Limpar agora", bg="#3d518d", fg="white", width=16, command=on_confirm).pack(side="left", padx=10)
    tk.Button(frame_botoes, text="Não limpar agora", bg="#d9534f", fg="white", width=16, command=on_cancel).pack(side="right", padx=10)

# --- Funções para manipular lista de pastas usando paths_config ---
def atualizar_lista_pastas():
    lista_pastas.delete(0, tk.END)
    pastas = carregar_pastas()
    pastas_normalizadas = [os.path.abspath(p) for p in pastas]
    for pasta in pastas_normalizadas:
        lista_pastas.insert(tk.END, pasta)

def adicionar_nova_pasta():
    pasta = filedialog.askdirectory()
    if pasta:
        pasta_abs = os.path.abspath(pasta)
        adicionar_pasta(pasta_abs)  # Já salva no JSON na pasta AppData
        atualizar_lista_pastas()

def remover_pastas_selecionadas():
    selecionadas = list(lista_pastas.curselection())
    if not selecionadas:
        messagebox.showinfo("Aviso", "Selecione uma ou mais pastas para remover.")
        return

    selecionadas.reverse()  # Remove da lista de baixo para cima para não bagunçar índices
    for i in selecionadas:
        pasta = lista_pastas.get(i)
        remover_pasta(pasta)  # Já salva no JSON na pasta AppData
        lista_pastas.delete(i)

    # Não precisa salvar manualmente, pois remover_pasta já faz isso

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
       # tw.wm_attributes("-topmost", True)
        tw.wm_attributes("-alpha", 0.95)

        label = tk.Label(
            tw,
            text=self.text,
            justify='center',
            background="#6a81c5",     # branco suave
            foreground="#f5f5f5",     # texto escuro neutro
            relief='flat',
            #borderwidth=3,
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            wraplength=280
        )
        label.pack()
        tw.geometry(f"+{x}+{y}")

    def _on_leave(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# --- Interface gráfica ---
root = tk.Tk()
root.title("A u t o C l e a n e r  –  Limpeza Inteligente  1.4.4")
centralizar_janela(root, 800, 600)
root.configure(bg='#f5f5f5')
root.iconbitmap(recurso_caminho("assets/autocleaner-off.ico"))

style = ttk.Style()
style.theme_use("default")
style.configure("Custom.Horizontal.TProgressbar", 
                troughcolor="#e0e0e0", 
                background="#3d518d", 
                thickness=10,
                bordercolor="#f5f5f5")

frame = tk.Frame(root, bg="#f5f5f5")
frame.pack(padx=20, pady=20, fill="both", expand=True)

titulo = tk.Label(frame, text="A u t o C l e a n e r",
                  font=("Segoe UI", 14, "bold"), bg="#f5f5f5", fg="#3d518d")
titulo.pack(pady=(0, 10))

paragrafo = tk.Label(frame, text="⚠️ Atenção! As limpezas são irreversíveis.",
                     font=("Segoe UI", 10, "bold"), bg="#f5f5f5", fg="#cc4747")
paragrafo.pack(pady=(0, 5))

frame_pastas = tk.Frame(frame, bg="#f5f5f5")
frame_pastas.pack(pady=5, fill="both")

lista_pastas = tk.Listbox(frame_pastas, height=5, width=60, selectmode=tk.MULTIPLE)
lista_pastas.pack(side="left", padx=(0, 10), fill="x", expand=True)

scroll_pastas = tk.Scrollbar(frame_pastas)
scroll_pastas.pack(side="right", fill="y")
lista_pastas.config(yscrollcommand=scroll_pastas.set)
scroll_pastas.config(command=lista_pastas.yview)

btn_adicionar = tk.Button(frame, text="Adicionar pasta", command=adicionar_nova_pasta)
btn_adicionar.pack(pady=2)
ToolTip(btn_adicionar,
            'Algumas pastas podem estar ocultas.\n' \
            'Para visualizá-las, ative a opção "Itens ocultos" em "Explorador de arquivos > Exibir". ' \
            'Após, volte ao AutoCleaner e tente encontrar a pasta novamente.\n' \
            'Não resolvendo, verifique configurações ' \
            'da máquina e do usuário, ou contate o administrador de seu sistema.')
tk.Button(frame, text="Remover pasta selecionada", command=remover_pastas_selecionadas).pack(pady=2)
tk.Button(frame, text="Ver espaço ocupado", command=analisar).pack(pady=2)
tk.Button(frame, text="Limpar agora", command=limpar).pack(pady=2)

frame_tempo = tk.Frame(frame, bg="#f5f5f5")
frame_tempo.pack(pady=10)

tk.Label(frame_tempo, text="Limpeza automática a cada (minutos):", bg="#f5f5f5").pack(side="left")

intervalo_var = tk.IntVar(value=60)
spinbox_intervalo = tk.Spinbox(frame_tempo, from_=1, to=1440, textvariable=intervalo_var, width=5)
spinbox_intervalo.pack(side="left", padx=5)

contador_var = tk.StringVar(value="--:--")
label_contador = tk.Label(frame, textvariable=contador_var, font=("Consolas", 12), bg="#f5f5f5", fg="#d9534f")
label_contador.pack(pady=5)
progresso_var = tk.IntVar()
porcentagem_var = tk.StringVar(value="0%")

scheduler = Scheduler(callback=limpeza_automatica, intervalo_minutos=intervalo_var.get())

frame_botoes = tk.Frame(frame, bg="#f5f5f5")
frame_botoes.pack(pady=5)

def iniciar_scheduler():
    confirm = messagebox.askyesno(
        "ATENÇÃO!",
        "⚠️ Você está prestes a ativar o modo automático do AutoCleaner.\n\n"
        "Deseja continuar?"
    )
    if not confirm:
        return

    scheduler.atualizar_intervalo(intervalo_var.get())
    scheduler.set_contagem_callback(lambda tempo: contador_var.set(tempo))
    scheduler.iniciar()
    btn_iniciar.config(state="disabled")
    btn_parar.config(state="normal")

def parar_scheduler():
    scheduler.parar()
    contador_var.set("--:--")
    btn_iniciar.config(state="normal")
    btn_parar.config(state="disabled")

btn_iniciar = tk.Button(frame_botoes, text="Ativar limpeza automática", command=iniciar_scheduler, bg="#3d518d", fg="white")
btn_iniciar.grid(row=0, column=0, padx=5)
ToolTip(btn_iniciar,
            '💡 Dica:\n'
            'Use a Limpeza automática do AutoCleaner para limpar periodicamente pastas de arquivos temporários do Windows, ex.: ...\TEMP.')

btn_parar = tk.Button(frame_botoes, text="Desativar limpeza automática", command=parar_scheduler, bg="#e77972", fg="white", state="disabled")
btn_parar.grid(row=0, column=1, padx=5)

progress_frame = tk.Frame(frame, bg="#f5f5f5")
progress_frame.pack(fill="x", pady=(10, 5))

progress_bar = ttk.Progressbar(progress_frame, 
                               variable=progresso_var,
                               maximum=100, 
                               style="Custom.Horizontal.TProgressbar")
progress_bar.pack(fill="x", expand=True, side="left")

label_porcentagem = tk.Label(progress_frame, textvariable=porcentagem_var,
                             bg="#f5f5f5", fg="#3d518d", font=("Segoe UI", 10, "bold"), width=5)
label_porcentagem.pack(side="right", padx=5)

texto_resultado = tk.Text(frame, height=15, font=("Consolas", 10), wrap="word")
texto_resultado.pack(pady=10, fill="both", expand=True)

def atualizar_progresso(valor):
    progresso_var.set(valor)
    porcentagem_var.set(f"{valor}%")
    root.update_idletasks()

atualizar_lista_pastas()

root.mainloop()
