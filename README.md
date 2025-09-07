A u t o C l e a n e r  -  Limpeza inteligente

Executável para Windows, com automação.


Download: https://renatobrunogo.github.io/autocleanersite/


    Versão: 1.4.8

        ✅ Adicionar e remover pastas personalizadas;

        🔎 Verificar espaço ocupado (nº de arquivos e tamanho total);

        🧹 Limpeza manual das pastas com progresso e logs;

        ⏰ Agendamento de limpezas automáticas com contagem regressiva;

        📁 Armazenamento persistente de arquivo user_paths.json na pasta AppData\Local\AutoCleaner;

        ⚠️ Avisos de confirmação para ações irreversíveis;

        📦 Empacotamento com PyInstaller (--onefile + --windowed) e ícone personalizado.

        
        Observações
            Todos os arquivos e subpastas das pastas selecionadas são deletados definitivamente;
            A limpeza automática não executa em segundo plano com o app fechado (não é um serviço).


        Skills

            -> Python 3.10+;
            -> Tkinter – GUI nativa para desktop;
            -> OS / shutil / threading – manipulação de arquivos, diretórios e execução assíncrona;
            -> JSON – persistência das pastas selecionadas;
            -> PyInstaller – empacotamento do .exe.

        
        Requisitos

            -> Sem necessidade de instalação;
            -> Windows 10 ou superior;
            -> Python 3.10+ (para desenvolvimento);
            -> Permissões de leitura/escrita nas pastas selecionadas.


        Estrutura do projeto

            -> O arquivo com as pastas escolhidas é salvo automaticamente em:
            
                <%LOCALAPPDATA%\AutoCleaner\user_paths.json>


            AutoCleaner/
            │
            ├── app/
            │   ├── main.py
            │   ├── analyzer.py
            │   ├── cleaner.py
            │   ├── scheduler.py
            │   ├── paths_config.py
            │   └── assets/
            │       └── autocleaner-off.ico
            │
            ├── dist/
            │   └── autocleaner-v0.0.0.exe
