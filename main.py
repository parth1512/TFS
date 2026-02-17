import sys
import threading
import queue
import logging
import time

from logger import logger, log_queue
from config_loader import config_loader
from excel_reader import excel_reader
from modbus_server import modbus_server

# Try importing Tkinter
try:
    import tkinter as tk
    from tkinter import scrolledtext, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    logger.warning("Tkinter not found. Running in Headless (Console) Mode.")

class ConsoleApp:
    def __init__(self):
        self.running = True
        print("=== Modbus Slave App (Headless Mode) ===")
        print("Commands: start, stop, status, quit")
        self.start_input_loop()

    def start_input_loop(self):
        # Start log printer thread
        threading.Thread(target=self.print_logs, daemon=True).start()
        
        while self.running:
            try:
                cmd = input("> ").strip().lower()
                if cmd == "start":
                    self.start_services()
                elif cmd == "stop":
                    self.stop_services()
                elif cmd == "status":
                    self.check_status()
                elif cmd == "quit" or cmd == "exit":
                    self.stop_services()
                    self.running = False
                    sys.exit(0)
                else:
                    print("Unknown command. Use: start, stop, status, quit")
            except (KeyboardInterrupt, EOFError):
                 self.stop_services()
                 sys.exit(0)

    def start_services(self):
        try:
            excel_reader.start()
            # modbus_server.start_server() spawns its own daemon thread.
            modbus_server.start_server()
            print("Services STARTED.")
        except Exception as e:
            print(f"Error starting services: {e}")

    def stop_services(self):
        try:
            excel_reader.stop()
            modbus_server.stop_server()
            print("Services STOPPED.")
        except Exception as e:
            print(f"Error stopping services: {e}")

    def check_status(self):
        # Simple check based on threads (heuristic)
        print(f"Modbus Server Running: {modbus_server.is_running}")
        print(f"Excel Reader Running: {excel_reader.running}")

    def print_logs(self):
        while self.running:
            try:
                record = log_queue.get(timeout=1)
                print(f"[LOG] {time.strftime('%H:%M:%S', time.localtime(record.created))} - {record.levelname} - {record.msg}")
            except queue.Empty:
                continue

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Modbus Slave")
        self.root.geometry("600x500")

        self.create_widgets()
        
        # Start Log Monitoring
        self.root.after(100, self.process_log_queue)
        
        # Load Config Init
        self.load_config_to_ui()

    def create_widgets(self):
        # Top Frame: Controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.btn_start = tk.Button(control_frame, text="Start Server", bg="green", fg="white", command=self.start_services)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(control_frame, text="Stop Server", bg="red", fg="white", command=self.stop_services, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        self.lbl_status = tk.Label(control_frame, text="Status: Stopped", fg="red")
        self.lbl_status.pack(side=tk.LEFT, padx=20)

        # Config Display
        config_frame = tk.LabelFrame(self.root, text="Current Configuration")
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        self.txt_config = tk.Text(config_frame, height=8, width=70)
        self.txt_config.pack(padx=5, pady=5)
        self.txt_config.config(state=tk.DISABLED) # Read-only

        # Log Window
        log_frame = tk.LabelFrame(self.root, text="Logs")
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.txt_log = scrolledtext.ScrolledText(log_frame, state=tk.DISABLED)
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_config_to_ui(self):
        conf = config_loader.load_config()
        import json
        pretty_conf = json.dumps(conf, indent=2)
        
        self.txt_config.config(state=tk.NORMAL)
        self.txt_config.delete(1.0, tk.END)
        self.txt_config.insert(tk.END, pretty_conf)
        self.txt_config.config(state=tk.DISABLED)

    def process_log_queue(self):
        try:
            while True:
                record = log_queue.get_nowait()
                msg = self.format_log(record)
                self.txt_log.config(state=tk.NORMAL)
                self.txt_log.insert(tk.END, msg + "\n")
                self.txt_log.see(tk.END)
                self.txt_log.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)

    def format_log(self, record):
        # Simple formatter from record
        return f"{time.strftime('%H:%M:%S', time.localtime(record.created))} - {record.levelname} - {record.msg}"

    def start_services(self):
        try:
            excel_reader.start()
            # modbus_server.start_server() spawns its own daemon thread.
            modbus_server.start_server()
            
            self.lbl_status.config(text="Status: Running", fg="green")
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            logger.info("Services started.")
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            messagebox.showerror("Error", str(e))

    def stop_services(self):
        try:
            excel_reader.stop()
            modbus_server.stop_server()
            
            self.lbl_status.config(text="Status: Stopped", fg="red")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            logger.info("Services stopped.")
        except Exception as e:
            logger.error(f"Failed to stop services: {e}")

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop_services()
            self.root.destroy()

if __name__ == "__main__":
    if TKINTER_AVAILABLE:
        root = tk.Tk()
        app = App(root)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
    else:
        # Fallback to Console App
        app = ConsoleApp()
