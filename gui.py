import tkinter as tk
from tkinter import ttk
import threading
import time
import datetime
import sys
import os
import ctypes
import subprocess
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import gc

from defender import Defender
from monitor import Monitor

class CyberShieldGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CyberShield - Blindagem de Acesso")
        self.root.geometry("600x560")
        self.root.configure(bg="#121214")
        self.root.resizable(False, False)
        
        # Variáveis de Estado
        self.blindagem_ativa = tk.BooleanVar(value=True)
        self.sistema_pausado = tk.BooleanVar(value=False)

        # Instanciar os componentes
        self.defender = Defender()
        self.monitor = Monitor(self.on_threat_detected)
        
        # Setup do Tray Icon
        self.tray_icon = None
        self.setup_tray()
        
        self.setup_ui()
        self.update_shield_animation()
        
        # Iniciar rotina periódica de otimização de memória RAM
        self.run_periodic_memory_cleanup()
        
        # Iniciar monitoramento em segundo plano
        self.monitor.start()
        
        # Executar parada e desativação inicial dos serviços corporativos de acesso remoto
        if self.blindagem_ativa.get():
            self.defender.stop_vnc()
            self.defender.stop_anydesk()
            self.log_message("Serviços VNC e AnyDesk interrompidos e desativados na inicialização.")

    def setup_ui(self):
        # Frame Principal
        main_frame = tk.Frame(self.root, bg="#121214")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titulo
        title_lbl = tk.Label(main_frame, text="🛡️ CYBERSHIELD PRO", font=("Arial", 20, "bold"), bg="#121214", fg="#00F2FE")
        title_lbl.pack(pady=(0, 10))

        # Painel do Escudo (Central)
        self.shield_frame = tk.Frame(main_frame, bg="#1a1a1e", bd=2, relief="groove")
        self.shield_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(self.shield_frame, text="BLINDAGEM CORPORATIVA ATIVA", font=("Arial", 14, "bold"), bg="#1a1a1e", fg="#4EED75")
        self.status_label.pack(pady=15)
        
        # Monitoramento Ativo de Serviços (Esclarecimento de processos ativos)
        self.services_frame = tk.LabelFrame(
            main_frame, text=" Monitoramento Ativo de Serviços de Sistema ", 
            font=("Arial", 10, "bold"), bg="#121214", fg="#00F2FE", bd=1, labelanchor="n"
        )
        self.services_frame.pack(fill=tk.X, pady=10)
        
        # Grid para os serviços
        self.services_frame.columnconfigure(0, weight=1)
        self.services_frame.columnconfigure(1, weight=1)
        
        # VNC Status Card
        self.vnc_card = tk.Frame(self.services_frame, bg="#1a1a1e", padx=10, pady=5)
        self.vnc_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.vnc_title = tk.Label(self.vnc_card, text="VNC SERVER (uvnc_service)", font=("Arial", 9, "bold"), bg="#1a1a1e", fg="#A4A4A4")
        self.vnc_title.pack()
        self.vnc_status = tk.Label(self.vnc_card, text="DESATIVADO (Serviço Parado)", font=("Arial", 8, "bold"), bg="#1a1a1e", fg="#00F2FE")
        self.vnc_status.pack()
        
        # AnyDesk Status Card
        self.any_card = tk.Frame(self.services_frame, bg="#1a1a1e", padx=10, pady=5)
        self.any_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.any_title = tk.Label(self.any_card, text="ANYDESK (AnyDesk Service)", font=("Arial", 9, "bold"), bg="#1a1a1e", fg="#A4A4A4")
        self.any_title.pack()
        self.any_status = tk.Label(self.any_card, text="DESATIVADO (Serviço Parado)", font=("Arial", 8, "bold"), bg="#1a1a1e", fg="#4EED75")
        self.any_status.pack()

        # Controles
        control_frame = tk.Frame(main_frame, bg="#121214")
        control_frame.pack(fill=tk.X, pady=10)
        
        # Botão de Blindagem Ativa
        self.btn_blindagem = tk.Checkbutton(
            control_frame, text="Blindagem Ativa (Bloqueio Automático)", variable=self.blindagem_ativa,
            font=("Arial", 11), bg="#121214", fg="#E1E1E6", selectcolor="#1a1a1e", activebackground="#121214", activeforeground="#E1E1E6"
        )
        self.btn_blindagem.pack(side=tk.LEFT, padx=10)
        
        # Botão de Pausar Sistema (Para o Help Desk)
        self.btn_pause = tk.Button(
            control_frame, text="PAUSAR PROTEÇÃO", font=("Arial", 10, "bold"),
            bg="#FF4949", fg="white", command=self.toggle_pause, relief="flat", padx=10
        )
        self.btn_pause.pack(side=tk.RIGHT, padx=10)

        # Histórico (Log)
        log_frame = tk.Frame(main_frame, bg="#1a1a1e")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(log_frame, text="Últimos Incidentes:", font=("Arial", 11), bg="#1a1a1e", fg="#A4A4A4").pack(anchor="w", padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, height=6, bg="#0d0d0f", fg="#A4A4A4", font=("Consolas", 9), state="disabled", bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Startup Button
        startup_frame = tk.Frame(main_frame, bg="#121214")
        startup_frame.pack(fill=tk.X, pady=(10, 0))
        btn_startup = tk.Button(
            startup_frame, text="🔑 Adicionar ao Iniciar do Windows (Silencioso/Admin)", 
            command=self.add_to_startup, bg="#1a1a1e", fg="#E1E1E6", relief="flat", font=("Arial", 9)
        )
        btn_startup.pack(side=tk.LEFT)
        
        self.log_message("Sistema de segurança corporativo pronto e monitorando em nível Admin.")

    def log_message(self, message):
        """Adiciona uma mensagem ao log na interface de forma controlada."""
        now = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{now}] {message}\n"
        
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, formatted)
        
        # Limita o histórico na tela a 100 linhas para evitar consumo infinito de RAM
        num_lines = int(self.log_text.index('end-1c').split('.')[0])
        if num_lines > 100:
            self.log_text.delete('1.0', '2.0')
            
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def toggle_pause(self):
        """Alterna o estado de pausa do sistema"""
        if self.sistema_pausado.get():
            self.sistema_pausado.set(False)
            self.monitor.pause(False)
            self.btn_pause.config(text="PAUSAR PROTEÇÃO", bg="#FF4949")
            self.status_label.config(text="BLINDAGEM CORPORATIVA ATIVA", fg="#4EED75")
            self.vnc_status.config(text="DESATIVADO (Serviço Parado)", fg="#00F2FE")
            self.any_status.config(text="DESATIVADO (Serviço Parado)", fg="#4EED75")
            
            self.defender.stop_vnc()
            self.defender.stop_anydesk()
            self.log_message("Sistema de proteção RETOMADO. Serviços de acesso parados e desativados.")
        else:
            self.sistema_pausado.set(True)
            self.monitor.pause(True)
            self.btn_pause.config(text="RETOMAR PROTEÇÃO", bg="#4EED75")
            self.status_label.config(text="SISTEMA PAUSADO (Vulnerável)", fg="#A4A4A4")
            self.vnc_status.config(text="PAUSADO (Serviço Ativo)", fg="#FF4949")
            self.any_status.config(text="PAUSADO (Serviço Ativo)", fg="#FF4949")
            
            self.defender.start_vnc()
            self.defender.start_anydesk()
            self.log_message("Sistema de proteção PAUSADO. Serviços reativados para o suporte técnico.")
        # Limpeza imediata de memória após mudança de estado
        gc.collect()

    def on_threat_detected(self, threat_source, details):
        """Chamado pelo Monitor quando uma ameaça é detectada."""
        if self.sistema_pausado.get():
            return
            
        def _update_gui():
            self.status_label.config(text=f"ALERTA: {threat_source}", fg="#FF4949")
            is_active_defense = self.blindagem_ativa.get()
            action = self.defender.trigger_defense(threat_source, is_active_defense)
            self.log_message(f"Acesso/Processo detectado: {threat_source}. Defesa: {action}")
            
            def _reset_status():
                if not self.sistema_pausado.get():
                    self.status_label.config(text="BLINDAGEM CORPORATIVA ATIVA", fg="#4EED75")
            self.root.after(10000, _reset_status)

        self.root.after(0, _update_gui)

    def update_shield_animation(self):
        """Faz a cor do status piscar/pulsar se não estiver pausado."""
        if not self.sistema_pausado.get() and "BLINDAGEM" in self.status_label.cget("text"):
            current_color = self.status_label.cget("fg")
            next_color = "#00F2FE" if current_color == "#4EED75" else "#4EED75"
            self.status_label.config(fg=next_color)
            
        self.root.after(1500, self.update_shield_animation)

    def create_tray_image(self):
        """Desenha um escudo otimizado de tamanho reduzido (32x32 pixels) para economizar RAM."""
        image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        # Escudo azul e branco otimizado
        dc.polygon([(16, 2), (28, 7), (28, 20), (16, 29), (4, 20), (4, 7)], fill="#00F2FE", outline="white", width=1)
        dc.polygon([(16, 5), (25, 9), (25, 18), (16, 26), (7, 18), (7, 9)], fill="#121214")
        dc.line([(12, 16), (15, 19), (21, 12)], fill="#4EED75", width=2)
        return image

    def setup_tray(self):
        """Inicia e mantém o ícone da bandeja em segundo plano"""
        image = self.create_tray_image()
        menu = pystray.Menu(
            item('Exibir Painel', self.restore_window, default=True),
            item('Sair do CyberShield', self.quit_application)
        )
        self.tray_icon = pystray.Icon("CyberShield", image, "CyberShield PRO", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_window(self, icon=None, item=None):
        """Restaura a janela na thread principal do Tkinter"""
        self.root.after(0, self.root.deiconify)
        self.root.after(0, self.root.focus_force)
        gc.collect()

    def minimize_to_tray(self):
        """Oculta a janela e envia para a bandeja"""
        self.root.withdraw()
        self.log_message("Minimizado para a bandeja oculta.")
        gc.collect()

    def run_periodic_memory_cleanup(self):
        """Coleta lixo da memória (Garbage Collection) a cada 30 segundos para manter RAM reduzida."""
        gc.collect()
        if not self.root.winfo_exists():
            return
        self.root.after(30000, self.run_periodic_memory_cleanup)

    def quit_application(self, icon=None, item=None):
        """Termina totalmente o aplicativo"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.monitor.stop()
        self.root.after(0, self.root.destroy)
        sys.exit(0)

    def add_to_startup(self):
        """Cria uma tarefa agendada silenciosa no Windows."""
        try:
            if getattr(sys, 'frozen', False):
                filepath = sys.executable
                cmd = f'schtasks /create /tn "CyberShield" /tr "\\"{filepath}\\"" /sc onlogon /rl highest /f'
            else:
                filepath = os.path.abspath(__file__)
                pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
                cmd = f'schtasks /create /tn "CyberShield" /tr "\\"{pythonw_path}\\" \\"{filepath}\\"" /sc onlogon /rl highest /f'
            
            subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log_message("Tarefa Agendada criada! CyberShield iniciará de forma oculta/admin no logon do Windows.")
        except Exception as e:
            self.log_message(f"Erro ao configurar inicialização silenciosa via Agendador: {e}")

    def on_closing(self):
        """Intercepta o clique de fechar (X) e minimiza"""
        self.minimize_to_tray()

def is_admin():
    """Verifica se o processo atual possui privilégios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        try:
            script_path = os.path.abspath(__file__)
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}"', None, 1)
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao solicitar elevação de privilégios: {e}")
            sys.exit(1)

    root = tk.Tk()
    app = CyberShieldGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
