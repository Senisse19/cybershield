# 🛡️ CyberShield PRO

**CyberShield PRO** é um sistema de blindagem defensiva corporativo de alto desempenho, projetado para proteger estações de trabalho Windows contra acessos remotos não autorizados (como **VNC**, **AnyDesk** e **RDP**).

O projeto é focado em **desempenho extremo**, utilizando chamadas nativas de baixo nível ao kernel do Windows para manter o uso de processamento em **0% estável** e liberar memória RAM ativamente, funcionando de forma invisível e silenciosa na bandeja de ícones ocultos do sistema (**System Tray**).

---

## ✨ Recursos Principais

*   **🔒 Blindagem de Acesso Ativa (VNC e AnyDesk):** Altera o tipo de inicialização dos serviços de sistema do VNC (`uvnc_service`) e AnyDesk (`AnyDesk Service`) para *Desativado (Disabled)* e derruba os processos em execução imediatamente.
*   **🔌 Liberação Inteligente para Help Desk:** Permite pausar temporariamente a proteção com um único clique. Os serviços de acesso remoto são reconfigurados para *Automático* e iniciados instantaneamente para o técnico de TI trabalhar. Ao finalizar, basta um clique para blindar a máquina novamente.
*   **👁️ Monitoramento Nativo de Baixo Nível (Zero Subprocessos):** Substitui as chamadas lentas de linha de comando por consultas nativas de rede e processos escritas em C (através do `psutil`). Isso garante **CPU em 0.0%** estável e zero picos de memória.
*   **💻 Tela de Bloqueio em Tela Cheia (Fullscreen Lock Screen):** Quando um acesso não autorizado é detectado, o sistema derruba o software invasor na hora e bloqueia a tela inteira com um painel de segurança de privilégio elevado. O cursor do mouse é travado e o computador só pode ser desbloqueado localmente digitando a senha padrão (`1234`).
*   **📥 Minimização Nativa para a Bandeja (System Tray):** Ao clicar no botão de fechar (**X**) da janela, o aplicativo oculta-se silenciosamente no menu de ícones ocultos da barra de tarefas do Windows. Um ícone de escudo dinâmico permite restaurar o painel ou fechar o programa com o botão direito.
*   **🔑 Inicialização Oculta com Privilégios Elevados (Sem UAC Prompts):** Permite adicionar o CyberShield para iniciar junto com o Windows de forma invisível no logon, criando uma Tarefa Agendada nativa no Agendador de Tarefas do Windows rodando em privilégio máximo (`Highest Privilege`).

---

## 📂 Estrutura do Projeto

*   `gui.py`: Painel de interface gráfica moderno (Tkinter) com design escuro, animações pulsantes de blindagem, gerenciamento de logs limitados a 100 linhas (economiza RAM), ícone de bandeja (`pystray`) e Garbage Collection periódico (a cada 30s).
*   `monitor.py`: Monitoramento assíncrono em Threads que vigia logs locais do AnyDesk, conexões TCP abertas nas portas 5900/5800 (VNC) e 3389 (RDP), e varredura proativa de processos em memória.
*   `defender.py`: Módulo executor de ações administrativas e tela de bloqueio com aprisionamento de mouse e senha de desbloqueio.
*   `.gitignore`: Filtra o repositório impedindo o envio de caches Python, temporários e executáveis.

---

## 🛠️ Como Compilar o Executável Único

Você pode compilar todo o projeto em um executável autônomo `.exe` de ~35MB que funciona sem exibir prompts pretos de terminal.

### Pré-requisitos
Certifique-se de ter o Python instalado e as seguintes bibliotecas no seu ambiente:
```bash
pip install psutil pystray pillow pywin32 pyinstaller
```

### Comando de Compilação
Abra o terminal no diretório do projeto e execute:
```bash
py -m PyInstaller --onefile --noconsole --name="CyberShield" gui.py
```

O executável pronto estará disponível na pasta `./dist/CyberShield.exe`.

---

## 🚀 Como Executar

1.  Abra a pasta `dist` e execute o arquivo `CyberShield.exe`.
2.  O sistema solicitará privilégios de administrador uma única vez (necessário para conseguir desativar e parar os serviços do Windows de VNC e AnyDesk).
3.  Uma vez aberto, sinta-se livre para clicar em **🔑 Adicionar ao Iniciar do Windows** para que o programa vigie seu computador silenciosamente a partir do momento em que você liga a máquina.
4.  Ao fechar no **X**, a janela sumirá e o escudo protetor estará ativo na sua bandeja de sistema!

---

## 🔒 Senha de Desbloqueio Padrão

*   **Senha local de emergência:** `1234`
