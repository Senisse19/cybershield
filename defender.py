import os
import sys
import ctypes
import winsound
import time
import threading
import tkinter as tk
from tkinter import ttk
import subprocess
import psutil
import gc

class Defender:
    def __init__(self):
        self.lock_window = None
        # Utilizaremos o SAPI nativo do Windows para Text-to-Speech
        try:
            import win32com.client
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        except Exception as e:
            print(f"Aviso: Text-to-Speech não disponível ({e}). Usando apenas beeps.")
            self.speaker = None

    def is_admin(self):
        """Verifica se o processo atual possui privilégios de administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def play_alert_sound(self):
        """Toca um sinal sonoro de alarme"""
        for _ in range(3):
            winsound.Beep(1000, 300)
            time.sleep(0.1)

    def speak(self, text):
        """Fala um texto em português através da voz nativa do Windows"""
        if self.speaker:
            try:
                def _speak():
                    self.speaker.Speak(text)
                t = threading.Thread(target=_speak, daemon=True)
                t.start()
            except Exception:
                pass

    def kill_processes_by_name(self, process_name):
        """Finaliza todos os processos com um determinado nome de forma extremamente otimizada em nível de API."""
        killed_any = False
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                    proc.kill()
                    killed_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        # Limpeza de memória imediata
        gc.collect()
        return killed_any

    def stop_vnc(self):
        """Para e desativa o serviço uvnc_service corporativo de forma robusta."""
        if not self.is_admin():
            print("Necessário privilégios de Administrador para parar o VNC.")
            return False
        try:
            # Configura como desativado e para o serviço
            subprocess.run(["sc", "config", "uvnc_service", "start=", "disabled"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["net", "stop", "uvnc_service"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Força o encerramento dos executáveis de forma nativa e sem spawns de shell extras
            self.kill_processes_by_name("winvnc.exe")
            self.kill_processes_by_name("tvnserver.exe")
            return True
        except Exception as e:
            print(f"Erro ao parar VNC: {e}")
            return False

    def start_vnc(self):
        """Reativa e inicia o serviço uvnc_service para o Help Desk poder acessar."""
        if not self.is_admin():
            print("Necessário privilégios de Administrador para iniciar o VNC.")
            return False
        try:
            subprocess.run(["sc", "config", "uvnc_service", "start=", "auto"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["net", "start", "uvnc_service"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except Exception as e:
            print(f"Erro ao iniciar VNC: {e}")
            return False

    def stop_anydesk(self):
        """Para e desativa o serviço AnyDesk e força o fechamento de qualquer executável."""
        if not self.is_admin():
            self.kill_processes_by_name("AnyDesk.exe")
            return False
        try:
            subprocess.run(["sc", "config", "AnyDesk", "start=", "disabled"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["net", "stop", "AnyDesk"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Força encerramento de todos os executáveis na memória
            self.kill_processes_by_name("AnyDesk.exe")
            return True
        except Exception as e:
            print(f"Erro ao parar AnyDesk: {e}")
            return False

    def start_anydesk(self):
        """Reativa e inicia o serviço do AnyDesk para liberação do Help Desk."""
        if not self.is_admin():
            return False
        try:
            subprocess.run(["sc", "config", "AnyDesk", "start=", "auto"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["net", "start", "AnyDesk"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except Exception as e:
            print(f"Erro ao iniciar AnyDesk: {e}")
            return False

    def show_fullscreen_lock(self, threat_source):
        """Abre uma tela cheia vermelha de bloqueio com controle total de mouse e senha."""
        if self.lock_window and self.lock_window.winfo_exists():
            return
            
        def _lock_screen():
            self.lock_window = tk.Tk()
            self.lock_window.overrideredirect(True)
            self.lock_window.attributes("-topmost", True)
            self.lock_window.attributes("-fullscreen", True)
            self.lock_window.configure(bg="#450a0a")
            self.lock_window.protocol("WM_DELETE_WINDOW", lambda: None)
            
            screen_width = self.lock_window.winfo_screenwidth()
            screen_height = self.lock_window.winfo_screenheight()
            
            container = tk.Frame(self.lock_window, bg="#450a0a")
            container.pack(expand=True)
            
            title = tk.Label(
                container, text="🔒 CYBERSHIELD - ACESSO BLOQUEADO 🔒", 
                font=("Arial", 28, "bold"), fg="#f87171", bg="#450a0a"
            )
            title.pack(pady=20)
            
            desc = tk.Label(
                container, 
                text=f"Um acesso remoto via {threat_source} foi detectado e bloqueado por segurança.\n"
                     f"A tela foi bloqueada para proteger suas informações confidenciais.",
                font=("Arial", 16), fg="#fca5a5", bg="#450a0a"
            )
            desc.pack(pady=20)
            
            info = tk.Label(
                container, 
                text="Para desbloquear localmente:\n"
                     "1. Use [TAB] para focar no campo abaixo.\n"
                     "2. Digite a senha (1234) e aperte [ENTER].",
                font=("Arial", 12), fg="#e7e5e4", bg="#450a0a"
            )
            info.pack(pady=10)
            
            pwd_frame = tk.Frame(container, bg="#450a0a")
            pwd_frame.pack(pady=15)
            
            tk.Label(pwd_frame, text="Senha:", font=("Arial", 14), fg="white", bg="#450a0a").pack(side=tk.LEFT, padx=5)
            pwd_entry = tk.Entry(pwd_frame, font=("Arial", 16), show="*", width=15, bg="#1c1917", fg="white", insertbackground="white")
            pwd_entry.pack(side=tk.LEFT, padx=5)
            pwd_entry.focus_set()
            
            error_lbl = tk.Label(container, text="", font=("Arial", 12, "bold"), fg="#f87171", bg="#450a0a")
            error_lbl.pack(pady=10)
            
            def attempt_unlock(event=None):
                if pwd_entry.get() == "1234":
                    self.lock_window.destroy()
                    self.lock_window = None
                    self.speak("Acesso local liberado.")
                    gc.collect()
                else:
                    error_lbl.config(text="Senha incorreta!")
                    pwd_entry.delete(0, tk.END)
                    
            pwd_entry.bind("<Return>", attempt_unlock)
            
            def lock_mouse():
                if self.lock_window and self.lock_window.winfo_exists():
                    try:
                        ctypes.windll.user32.SetCursorPos(screen_width // 2, screen_height // 2)
                    except:
                        pass
                    self.lock_window.after(100, lock_mouse)
                    
            lock_mouse()
            self.lock_window.mainloop()
            
        t = threading.Thread(target=_lock_screen, daemon=True)
        t.start()

    def trigger_defense(self, threat_source, active_protection=False):
        """Aciona a defesa com base na ameaça."""
        msg = f"ALERTA! Acesso remoto via {threat_source} detectado!"
        print(msg)
        
        self.play_alert_sound()
        # self.speak(f"Aviso! Acesso remoto via {threat_source} detectado.") # Desativado a pedido do usuário
        
        # Chama a tela de bloqueio vermelha em tela cheia!
        self.show_fullscreen_lock(threat_source)
        
        if active_protection:
            if threat_source == "AnyDesk":
                # self.speak("Interrompendo serviço AnyDesk.") # Desativado
                self.stop_anydesk()
                return "Desativado & Fechado"
            elif threat_source == "VNC":
                # self.speak("Interrompendo serviço VNC corporativo.") # Desativado
                self.stop_vnc()
                return "Desativado & Fechado"
            elif threat_source == "RDP":
                try:
                    subprocess.run(["powershell", "-Command", r"query session | Select-String -Pattern 'rdp-tcp#' | ForEach-Object { $id = ($_ -split '\s+')[2]; if ($id -match '\d+') { logoff $id } }"], creationflags=subprocess.CREATE_NO_WINDOW)
                except:
                    pass
                return "Sessão RDP Encerrada"
        return "Registrado"
