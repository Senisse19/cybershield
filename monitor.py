import os
import time
import threading
import psutil

class Monitor:
    def __init__(self, callback):
        """
        callback: Função que será chamada quando uma ameaça for detectada.
                  Assinatura: callback(threat_source, details)
        """
        self.callback = callback
        self.running = False
        self.paused = False
        
        # Caminhos conhecidos de trace de conexões do AnyDesk
        self.anydesk_log_paths = [
            os.path.join(os.environ.get('ProgramData', 'C:\\ProgramData'), 'AnyDesk', 'connection_trace.txt'),
            os.path.join(os.environ.get('APPDATA', ''), 'AnyDesk', 'connection_trace.txt')
        ]
        self.active_log_path = None
        self.last_log_size = 0

    def start(self):
        self.running = True
        self.paused = False
        
        # Iniciar threads de monitoramento ultraleves em segundo plano
        threading.Thread(target=self._monitor_anydesk_logs, daemon=True).start()
        threading.Thread(target=self._monitor_network_ports, daemon=True).start()
        threading.Thread(target=self._monitor_proactive_processes, daemon=True).start()

    def stop(self):
        self.running = False

    def pause(self, is_paused):
        self.paused = is_paused

    def _monitor_anydesk_logs(self):
        """Monitora o arquivo connection_trace.txt de forma passiva."""
        for path in self.anydesk_log_paths:
            if os.path.exists(path):
                self.active_log_path = path
                self.last_log_size = os.path.getsize(path)
                break
                
        if not self.active_log_path:
            return

        while self.running:
            if self.paused:
                time.sleep(2)
                continue

            try:
                current_size = os.path.getsize(self.active_log_path)
                if current_size > self.last_log_size:
                    with open(self.active_log_path, 'r', encoding='utf-16', errors='ignore') as f:
                        f.seek(self.last_log_size)
                        new_lines = f.readlines()
                        
                        for line in new_lines:
                            if "Incoming" in line or "I n c o m i n g" in line:
                                self.callback("AnyDesk", "Tentativa de conexão gravada no Log")
                                
                    self.last_log_size = current_size
                elif current_size < self.last_log_size:
                    self.last_log_size = current_size
            except Exception as e:
                pass
                
            time.sleep(1)

    def _monitor_network_ports(self):
        """Monitora conexões de rede em nível de Kernel (Zero subprocessos) usando psutil."""
        target_ports = {5900, 5800, 3389}
        
        while self.running:
            if self.paused:
                time.sleep(2)
                continue

            try:
                # Obtém conexões ativas TCP de forma nativa e extremamente rápida
                for conn in psutil.net_connections(kind='tcp'):
                    if conn.status == 'ESTABLISHED':
                        port = conn.laddr.port
                        if port in target_ports:
                            threat = "VNC" if port in {5900, 5800} else "RDP"
                            self.callback(threat, f"Conexão ativa na porta {port}")
                            time.sleep(8) # Evita disparo contínuo do mesmo alarme
                            break
            except Exception as e:
                pass
                
            time.sleep(2)

    def _monitor_proactive_processes(self):
        """Monitora processos em execução de forma nativa usando psutil."""
        while self.running:
            if self.paused:
                time.sleep(2)
                continue
                
            try:
                # Varredura de processos na memória via psutil (Consumo de CPU próximo a 0.0%)
                for proc in psutil.process_iter(['name']):
                    try:
                        name = proc.info['name']
                        if name and name.lower() == "anydesk.exe":
                            self.callback("AnyDesk", "Processo AnyDesk ativo na memória")
                            time.sleep(5)
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
            except Exception as e:
                pass
                
            time.sleep(2)
