import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sys
import os
import json
import threading
import subprocess
import urllib.request
import urllib.error
import shutil
from pathlib import Path
from tkinter import font
import requests
from update_manager import UpdateManager

# Handle PyInstaller bundled files
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INSTALLATION_FILE = "zsdumper_install.json"
CONFIG_FILE = "zsdumper_config.json"
UPDATE_API_URL = "https://api-zsdump.zinz1-dev.fr"

class StylishButton(tk.Button):
    """Bouton exact comme l'image"""
    def __init__(self, parent, text, command, 
                 bg="#00b894", hover_bg="#00cec9", 
                 fg="#ffffff", width=15, height=35, **kwargs):
        super().__init__(parent, text=text, command=command,
                        bg=bg, fg=fg,
                        relief="flat", cursor="hand2",
                        font=("Helvetica", 10, "bold"),
                        width=width, height=height, **kwargs)
        self.hover_bg = hover_bg
        self.original_bg = bg
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, event):
        self.config(bg=self.hover_bg)
        
    def on_leave(self, event):
        self.config(bg=self.original_bg)

class SidebarItem(tk.Button):
    """Élément de navigation sidebar style Electron"""
    def __init__(self, parent, text, icon, command, active=False):
        self.active = active
        bg_active = "#1b1725"  # Violet foncé comme l'Electron
        bg_inactive = "#0b0b0f"  # Fond sidebar
        fg_active = "#ffffff"
        fg_inactive = "#9999a8"
        
        super().__init__(parent, 
                        text=f"  {icon}  {text}", 
                        command=command,
                        bg=bg_active if active else bg_inactive,
                        fg=fg_active if active else fg_inactive,
                        relief="flat", cursor="hand2",
                        font=("Manrope", 11, "bold"),
                        anchor="w", padx=12, pady=11)
        
        self.bg_active = bg_active
        self.bg_inactive = bg_inactive
        self.fg_active = fg_active
        self.fg_inactive = fg_inactive
        self.hover_bg = "#1a1a22"
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, event):
        if not self.active:
            self.config(bg=self.hover_bg, fg="#ffffff")
            
    def on_leave(self, event):
        if not self.active:
            self.config(bg=self.bg_inactive, fg=self.fg_inactive)
            
    def set_active(self, active):
        self.active = active
        if active:
            self.config(bg=self.bg_active, fg=self.fg_active)
        else:
            self.config(bg=self.bg_inactive, fg=self.fg_inactive)

class ModernEntry(tk.Entry):
    """Champ de saisie style Electron"""
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, 
                        bg="#15151c", fg="#f5f5f7",
                        insertbackground="#9b72ff", relief="flat",
                        font=("Manrope", 10), **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "#636e72"
        self.normal_color = "#f5f5f7"
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        
        if placeholder:
            self.insert(0, placeholder)
            self.config(fg=self.placeholder_color)
            
    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.normal_color)
            
    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

class ZSDumperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZS Dumper — Control Center")
        self.geometry("1450x920")
        self.configure(bg="#08080b")
        self.resizable(True, True)
        
        # Palette de couleurs exacte de l'application Electron
        self.colors = {
            'bg': '#08080b',              # Fond très sombre
            'bg_dark': '#050507',         # Fond ultra sombre
            'sidebar': '#0b0b0f',         # Sidebar
            'sidebar_light': '#1a1a22',   # Sidebar light
            'card': '#101015',            # Cartes
            'card_light': '#15151c',      # Cartes plus claires
            'card_hover': '#1b1725',      # Cartes au survol
            'purple': '#9b72ff',          # Violet principal
            'purple_light': '#b38aff',    # Violet clair
            'purple_dark': '#7c3aed',     # Violet foncé
            'green': '#57e39b',           # Vert accent
            'green_light': '#7df0b2',     # Vert clair
            'line': '#292934',           # Lignes
            'muted': '#858595',           # Texte atténué
            'text': '#f5f5f7',            # Texte principal
            'text_muted': '#767686',      # Texte gris
            'text_dark': '#636e72',       # Texte gris foncé
            'success': '#57e39b',         # Vert succès
            'error': '#ff9b9b',           # Rouge erreur
            'warning': '#ffb700',         # Orange attention
        }
        
        self.current_page = "dumper"
        self.targets = []
        self.config_data = {}
        self.update_manager = UpdateManager(CONFIG_FILE)
        
        self.setup_ui()
        self.check_installation()
        
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self, bg=self.colors['bg'])
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create sidebar and content
        self.setup_sidebar(main_container)
        
        # Main content area style Electron
        self.content_area = tk.Frame(main_container, bg=self.colors['bg'])
        self.content_area.pack(side="right", fill="both", expand=True, padx=0)
        
        # Show initial page
        self.show_dumper_page()
        
    def setup_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.colors['sidebar'], width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Header simple
        header_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        header_frame.pack(fill="x", pady=20, padx=20)
        
        tk.Label(header_frame, text="ZS Dumper", 
                bg=self.colors['sidebar'], fg=self.colors['text'],
                font=("Manrope", 16, "bold")).pack()
        
        # Navigation simple
        self.nav_buttons = {}
        
        nav_items = [
            ("Overview", "📊", self.show_dumper_page),
            ("Dumper", "⬇", self.show_dumper_page),
            ("Decrypt", "�", self.show_decrypt_page),
            ("Fixer", "🔧", self.show_fixer_page),
            ("Resources", "�", self.show_resources_page),
        ]
        
        nav_frame = tk.Frame(sidebar, bg=self.colors['sidebar'])
        nav_frame.pack(fill="x", padx=0)
        

        
        for text, icon, command in nav_items:
            active = (text == "Dumper")
            bg = "#1b1725" if active else "transparent"
            fg = self.colors['text'] if active else "#8d8d9c"
            
            btn = tk.Button(nav_frame, text=text, command=command,
                           bg=bg, fg=fg,
                           relief="flat", cursor="hand2",
                           font=("Manrope", 11, "bold" if active else "normal"),
                           anchor="w", padx=12, pady=10)
            btn.pack(fill="x", pady=2)
            self.nav_buttons[text] = btn

        
    def draw_electron_logo(self, canvas, x, y, size):
        """Logo style Electron - ZS avec violet"""
        # Fond violet foncé
        canvas.create_oval(x-size, y-size, x+size, y+size, 
                         fill="#1b1034", outline="")
        
        # Lettre Z
        canvas.create_text(x, y, text="Z", fill="#9b72ff",
                          font=("Manrope", 18, "bold"))
        
    def show_dumper_page(self):
        self.clear_content()
        self.set_active_nav("Dumper")
        
        # Content inner
        content_inner = tk.Frame(self.content_area, bg=self.colors['bg'])
        content_inner.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Section heading simple
        section_heading = tk.Frame(content_inner, bg=self.colors['bg'])
        section_heading.pack(fill="x", pady=(0, 25))
        
        tk.Label(section_heading, text="Cibles", bg=self.colors['bg'], fg=self.colors['text'],
                font=("Manrope", 24, "bold")).pack(side="left")
        
        # Add target button petit
        add_btn = tk.Button(section_heading, text="+", 
                           command=self.show_add_target_modal,
                           bg="#9b72ff", fg="white",
                           relief="flat", cursor="hand2",
                           font=("Manrope", 14, "bold"), width=3, height=1)
        add_btn.pack(side="right")
        
        # New target card compact
        target_card = tk.Frame(content_inner, bg=self.colors['card'])
        target_card.pack(fill="x", pady=(0, 20), ipady=15)
        
        target_inner = tk.Frame(target_card, bg=self.colors['card'])
        target_inner.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Input fields compacts
        input_container = tk.Frame(target_inner, bg=self.colors['card'])
        input_container.pack(fill="x")
        
        name_frame = tk.Frame(input_container, bg=self.colors['card'])
        name_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.name_entry = ModernEntry(name_frame, placeholder="Nom")
        self.name_entry.pack(fill="x", ipady=8)
        
        ip_frame = tk.Frame(input_container, bg=self.colors['card'])
        ip_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.ip_entry = ModernEntry(ip_frame, placeholder="IP / CFX")
        self.ip_entry.pack(fill="x", ipady=8)
        
        # Action buttons petits
        tk.Button(input_container, text="Add", command=self.add_target,
                 bg="#9b72ff", fg="white",
                 relief="flat", cursor="hand2",
                 font=("Manrope", 10, "bold"), width=8).pack(side="right")
        
        # Targets list
        self.targets_list = tk.Frame(content_inner, bg=self.colors['bg'])
        self.targets_list.pack(fill="both", expand=True)
        
        self.add_sample_targets()
        
        # New target card - Design moderne avec texture
        target_card = tk.Frame(self.content_area, bg="#3d4852", 
                               highlightbackground="#00b894", highlightthickness=1)
        target_card.pack(fill="x", pady=(0, 30), padx=40, ipady=20)
        
        # Container interne
        inner_container = tk.Frame(target_card, bg="#3d4852")
        inner_container.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Card header
        tk.Label(inner_container, text="NOUVELLE CIBLE",
                bg="#3d4852", fg="#ffffff",
                font=("Helvetica", 17, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Input fields container
        input_container = tk.Frame(inner_container, bg="#3d4852")
        input_container.pack(fill="x")
        
        # Name field
        name_frame = tk.Frame(input_container, bg="#3d4852")
        name_frame.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        tk.Label(name_frame, text="NOM *", 
                bg="#3d4852", fg="#b2bec3",
                font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 8))
        
        self.name_entry = ModernEntry(name_frame, placeholder="Nom du serveur",
                                    highlightthickness=1, highlightbackground="#00b894",
                                    highlightcolor="#00b894")
        self.name_entry.pack(fill="x", ipady=12)
        
        # IP field
        ip_frame = tk.Frame(input_container, bg="#3d4852")
        ip_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(ip_frame, text="IP / CFX", 
                bg="#3d4852", fg="#b2bec3",
                font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 8))
        
        self.ip_entry = ModernEntry(ip_frame, placeholder="cfx.re/join/xxxxxx",
                                   highlightthickness=1, highlightbackground="#00b894",
                                   highlightcolor="#00b894")
        self.ip_entry.pack(fill="x", ipady=12)
        
        # Action buttons
        button_container = tk.Frame(inner_container, bg="#3d4852")
        button_container.pack(fill="x", pady=(20, 0))
        
        # Résoudre l'IP
        resolve_btn = tk.Button(button_container, text="Q Résoudre l'IP", 
                               command=self.resolve_ip,
                               bg="#4b5563", fg="#dfe6e9",
                               relief="flat", cursor="hand2",
                               font=("Helvetica", 10, "bold"), width=15,
                               activebackground="#00b894", activeforeground="white")
        resolve_btn.pack(side="left", padx=(0, 10))
        
        # Détection auto
        detect_btn = tk.Button(button_container, text="Détection auto", 
                              command=self.auto_detect,
                              bg="#4b5563", fg="#dfe6e9",
                              relief="flat", cursor="hand2",
                              font=("Helvetica", 10, "bold"), width=15,
                              activebackground="#00b894", activeforeground="white")
        detect_btn.pack(side="left", padx=(0, 10))
        
        # Ajouter
        add_btn = tk.Button(button_container, text="Ajouter", 
                          command=self.add_target,
                          bg="#00b894", fg="white",
                          relief="flat", cursor="hand2",
                          font=("Helvetica", 10, "bold"), width=12,
                          activebackground="#00cec9")
        add_btn.pack(side="right")
        
        # Auto detect checkbox
        checkbox_frame = tk.Frame(inner_container, bg="#3d4852")
        checkbox_frame.pack(fill="x", pady=(20, 0))
        
        self.auto_detect_var = tk.BooleanVar()
        checkbox = tk.Checkbutton(checkbox_frame, text="Détection auto",
                                 variable=self.auto_detect_var,
                                 bg="#3d4852", fg="#dfe6e9",
                                 selectcolor="#00b894", 
                                 activebackground="#3d4852",
                                 activeforeground="#ffffff", 
                                 font=("Helvetica", 10, "bold"),
                                 relief="flat", cursor="hand2")
        checkbox.pack(anchor="w")
        
        tk.Label(checkbox_frame, 
                text="Détection auto lit le process FiveM ouvert et récupère l'IP du serveur connecté ainsi que le token en mémoire.",
                bg="#3d4852", fg="#b2bec3",
                font=("Helvetica", 9), wraplength=800).pack(anchor="w", pady=(6, 0))
        
        # Targets list section - Design moderne
        list_container = tk.Frame(self.content_area, bg="#1e272e")
        list_container.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        # Targets header avec nombre de cibles
        targets_header = tk.Frame(list_container, bg="#1e272e")
        targets_header.pack(fill="x", pady=(0, 20))
        
        tk.Label(targets_header, text=f"{len(self.targets)} cibles",
                bg="#1e272e", fg="#b2bec3",
                font=("Helvetica", 13, "bold")).pack(side="left")
        
        # Search bar avec texture
        search_frame = tk.Frame(list_container, bg="#3d4852", 
                               highlightbackground="#00b894", highlightthickness=1)
        search_frame.pack(fill="x", pady=(0, 20), ipady=8)
        
        search_entry = ModernEntry(search_frame, placeholder="🔍",
                                   highlightthickness=1, highlightbackground="#00b894",
                                   highlightcolor="#00b894")
        search_entry.pack(fill="x", padx=15, ipady=10)
        
        # Targets list
        self.targets_list = tk.Frame(list_container, bg="#1e272e")
        self.targets_list.pack(fill="both", expand=True)
        
        # Add sample targets
        self.add_sample_targets()
        
    def add_sample_targets(self):
        sample_targets = [
            {"name": "new area", "ip": "204.10.193.13:30120", "token": "✔", "initial": "N"},
            {"name": "t-life", "ip": "play.t-life.fr", "token": "✔", "initial": "T"},
            {"name": "fm", "ip": "play.fm.fr", "token": "-", "initial": "F"},
            {"name": "pixelar", "ip": "play.pixelar.fr", "token": "✔", "initial": "P"},
            {"name": "17movement", "ip": "play.17movement.fr", "token": "-", "initial": "1"},
        ]
        
        for target in sample_targets:
            self.targets.append(target)
            self.create_target_item(target)
            
    def create_target_item(self, target):
        # Carte compacte
        item_card = tk.Frame(self.targets_list, bg=self.colors['card'])
        item_card.pack(fill="x", pady=5, ipady=10)
        
        inner_container = tk.Frame(item_card, bg=self.colors['card'])
        inner_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Nom
        tk.Label(inner_container, text=target['name'], 
                bg=self.colors['card'], fg=self.colors['text'],
                font=("Manrope", 12, "bold")).pack(side="left")
        
        # IP
        tk.Label(inner_container, text=target['ip'], 
                bg=self.colors['card'], fg=self.colors['muted'],
                font=("Manrope", 10)).pack(side="left", padx=15)
        
        # Dump button petit
        dump_btn = tk.Button(inner_container, text="Dump", 
                           command=lambda t=target: self.start_dump(t),
                           bg="#9b72ff", fg="white",
                           relief="flat", cursor="hand2",
                           font=("Manrope", 9, "bold"), width=6)
        dump_btn.pack(side="right")
        
    def show_add_target_modal(self):
        """Modal simple pour ajouter une cible"""
        self.modal_window = tk.Toplevel(self)
        self.modal_window.title("Add Target")
        self.modal_window.geometry("400x300")
        self.modal_window.configure(bg=self.colors['bg'])
        self.modal_window.resizable(False, False)
        self.modal_window.transient(self)
        self.modal_window.grab_set()
        
        self.modal_window.update_idletasks()
        x = (self.modal_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.modal_window.winfo_screenheight() // 2) - (300 // 2)
        self.modal_window.geometry(f"+{x}+{y}")
        
        # Modal content
        modal_inner = tk.Frame(self.modal_window, bg=self.colors['card'])
        modal_inner.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(modal_inner, text="Add target",
                bg=self.colors['card'], fg=self.colors['text'],
                font=("Manrope", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Name input
        tk.Label(modal_inner, text="Name", bg=self.colors['card'], fg=self.colors['muted'],
                font=("Manrope", 10)).pack(anchor="w")
        ModernEntry(modal_inner, placeholder="Name").pack(fill="x", pady=(0, 15), ipady=8)
        
        # IP input
        tk.Label(modal_inner, text="IP / CFX", bg=self.colors['card'], fg=self.colors['muted'],
                font=("Manrope", 10)).pack(anchor="w")
        ModernEntry(modal_inner, placeholder="IP").pack(fill="x", pady=(0, 20), ipady=8)
        
        # Add button
        tk.Button(modal_inner, text="Add", command=self.close_modal,
                 bg="#9b72ff", fg="white",
                 relief="flat", cursor="hand2",
                 font=("Manrope", 10, "bold"), width=10, pady=8).pack(anchor="e")
        
    def close_modal(self):
        if hasattr(self, 'modal_window') and self.modal_window:
            self.modal_window.destroy()
        
    def resolve_ip(self):
        ip = self.ip_entry.get()
        if ip and ip != "Ex : cfx.re/join/xxxxxx":
            try:
                if not ip.startswith("http"):
                    ip = "https://" + ip
                res = requests.get(ip, timeout=15)
                server_ip = res.headers.get("x-citizenfx-url")
                if server_ip:
                    self.ip_entry.delete(0, tk.END)
                    self.ip_entry.insert(0, server_ip.replace("http://", "").replace("/", ""))
                    messagebox.showinfo("Succès", f"IP résolue avec succès : {server_ip}")
                else:
                    messagebox.showwarning("Attention", "Impossible de résoudre l'IP")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la résolution : {str(e)}")
        else:
            messagebox.showwarning("Attention", "Veuillez entrer un lien cfx.re")
            
    def auto_detect(self):
        try:
            import auto
            token = auto.get_token()
            if token:
                messagebox.showinfo("Détection Auto", "Token FiveM détecté avec succès !")
            else:
                messagebox.showwarning("Attention", "Impossible de détecter le token FiveM")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la détection : {str(e)}")
            
    def add_target(self):
        name = self.name_entry.get()
        ip = self.ip_entry.get()
        
        if name and ip and name != "Ex : Mon FiveM Server" and ip != "Ex : cfx.re/join/xxxxxx":
            new_target = {
                "name": name,
                "ip": ip,
                "token": "-",
                "initial": name[0].upper()
            }
            self.targets.append(new_target)
            self.create_target_item(new_target)
            messagebox.showinfo("Succès", f"Cible '{name}' ajoutée avec succès !")
        else:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
            
    def start_dump(self, target):
        try:
            import auto
            
            ip = target['ip']
            token = auto.get_token()
            if not token:
                messagebox.showerror("Erreur", "Token non trouvé. Assurez-vous que FiveM est en cours d'exécution.")
                return
            
            base_url = "http://" + ip.replace("http://", "").replace("https://", "")
            dumper = auto.FiveMDumper(base_url, token, max_workers=15)
            
            self.show_dump_progress(target['name'])
            
            dumper.run()
            
            decryptor = auto.FiveMDecryptor()
            decryptor.start()
            
            import shutil
            for folder in ["Temp", "Unpacked", "TempCompiled", "Resources"]:
                if os.path.isdir(folder):
                    try:
                        shutil.rmtree(folder)
                    except:
                        pass
            
            messagebox.showinfo("Succès", f"Dump terminé pour {target['name']} !\nRésultats dans Output/")
            self.clear_dump_progress()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du dump : {str(e)}")
            self.clear_dump_progress()
            
    def show_dump_progress(self, target_name):
        self.progress_window = tk.Toplevel(self)
        self.progress_window.title("Dump en cours")
        self.progress_window.geometry("480x240")
        self.progress_window.configure(bg=self.colors['bg'])
        self.progress_window.resizable(False, False)
        self.progress_window.transient(self)
        self.progress_window.grab_set()
        
        self.progress_window.update_idletasks()
        x = (self.progress_window.winfo_screenwidth() // 2) - (480 // 2)
        y = (self.progress_window.winfo_screenheight() // 2) - (240 // 2)
        self.progress_window.geometry(f"+{x}+{y}")
        
        # Progress card
        progress_card = tk.Frame(self.progress_window, bg=self.colors['card'])
        progress_card.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(progress_card, text=f"Dump en cours : {target_name}",
                bg=self.colors['card'], fg=self.colors['text'],
                font=("Manrope", 16, "bold")).pack(pady=45)
        
        progress = ttk.Progressbar(progress_card, length=380, mode='indeterminate')
        progress.pack(pady=25)
        progress.start()
        
    def clear_dump_progress(self):
        if hasattr(self, 'progress_window') and self.progress_window:
            self.progress_window.destroy()
            
    def set_active_nav(self, active_text):
        for text, btn in self.nav_buttons.items():
            btn.set_active(text == active_text)
            
    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
    def show_decrypt_page(self):
        self.clear_content()
        self.set_active_nav("Decrypt")
        self.show_placeholder("Decrypt")
        
    def show_fixer_page(self):
        self.clear_content()
        self.set_active_nav("Fixer")
        self.show_placeholder("Fixer")
        
    def show_resources_page(self):
        self.clear_content()
        self.set_active_nav("Resources")
        self.show_placeholder("Resources")
        
    def show_placeholder(self, title):
        placeholder = tk.Frame(self.content_area, bg=self.colors['bg'])
        placeholder.pack(fill="both", expand=True)
        
        center_frame = tk.Frame(placeholder, bg=self.colors['bg'])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(center_frame, text=title, 
                bg=self.colors['bg'], fg=self.colors['text'],
                font=("Manrope", 32, "bold")).pack(pady=(0, 15))
        
        tk.Label(center_frame, text="Coming soon",
                bg=self.colors['bg'], fg=self.colors['muted'],
                font=("Manrope", 14)).pack()
        
    def check_installation(self):
        if os.path.exists(INSTALLATION_FILE):
            with open(INSTALLATION_FILE, 'r') as f:
                install_data = json.load(f)
            if install_data.get('installed'):
                self.config_data = install_data
                return
        
        self.show_installation()
        
    def show_installation(self):
        install_window = tk.Toplevel(self)
        install_window.title("Installation ZS Dumper")
        install_window.geometry("580x680")
        install_window.configure(bg=self.colors['bg'])
        install_window.resizable(False, False)
        install_window.transient(self)
        install_window.grab_set()
        
        install_window.update_idletasks()
        x = (install_window.winfo_screenwidth() // 2) - (580 // 2)
        y = (install_window.winfo_screenheight() // 2) - (680 // 2)
        install_window.geometry(f"+{x}+{y}")
        
        # Installation card
        install_card = tk.Frame(install_window, bg=self.colors['card'])
        install_card.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo
        logo_bg = tk.Frame(install_card, bg=self.colors['purple'], 
                          width=95, height=95)
        logo_bg.pack(pady=(35, 25))
        logo_bg.pack_propagate(False)
        
        logo_canvas = tk.Canvas(logo_bg, width=85, height=85, 
                               bg=self.colors['purple'], highlightthickness=0)
        logo_canvas.pack(pady=5)
        self.draw_electron_logo(logo_canvas, 42, 42, 38)
        
        tk.Label(install_card, text="ZS DUMPER",
                bg=self.colors['card'], fg=self.colors['text'],
                font=("Manrope", 28, "bold")).pack(pady=(0, 12))
        
        tk.Label(install_card, text="PROFESSIONAL",
                bg=self.colors['card'], fg=self.colors['purple_light'],
                font=("Manrope", 12, "bold")).pack(pady=(0, 35))
        
        tk.Label(install_card, text="Assistant d'installation",
                bg=self.colors['card'], fg=self.colors['muted'],
                font=("Manrope", 14)).pack(pady=(0, 30))
        
        # Log section
        log_frame = tk.Frame(install_card, bg=self.colors['sidebar'], 
                           highlightbackground=self.colors['purple'],
                           highlightthickness=2)
        log_frame.pack(fill="both", expand=True, padx=30, pady=12)
        
        log_text = scrolledtext.ScrolledText(log_frame, bg=self.colors['sidebar'], 
                                              fg=self.colors['text'], 
                                              font=("Consolas", 11),
                                              relief="flat", highlightthickness=0)
        log_text.pack(fill="both", expand=True, padx=18, pady=18)
        
        def add_log(message):
            log_text.insert(tk.END, f"[{self.get_timestamp()}] {message}\n")
            log_text.see(tk.END)
            
        def run_installation():
            try:
                add_log("✓ Vérification des prérequis...")
                
                java_installed = self.check_java()
                if not java_installed:
                    add_log("✗ Java non détecté")
                    messagebox.showerror("Erreur", "Java est requis pour l'installation.")
                    return
                
                add_log("✓ Java détecté avec succès")
                
                add_log("✓ Création des dossiers...")
                os.makedirs('Output', exist_ok=True)
                add_log("✓ Dossier Output créé")
                
                install_data = {
                    'installed': True,
                    'version': '2.0',
                    'edition': 'Professional',
                    'install_date': str(Path.cwd()),
                    'output_dir': str(Path.cwd() / 'Output'),
                    'java_version': self.get_java_version()
                }
                
                with open(INSTALLATION_FILE, 'w') as f:
                    json.dump(install_data, f)
                
                add_log("✓ Installation terminée avec succès")
                
                messagebox.showinfo("Installation", "ZS Dumper a été installé avec succès!")
                install_window.destroy()
                
                self.config_data = install_data
                
            except Exception as e:
                add_log(f"✗ Erreur : {str(e)}")
                messagebox.showerror("Erreur", f"Erreur lors de l'installation : {str(e)}")
        
        StylishButton(install_card, "Installer", run_installation,
                     bg=self.colors['purple'], hover_bg=self.colors['purple_light'],
                     width=28).pack(pady=30)
        
    def check_java(self):
        try:
            result = subprocess.run(["java", "-version"], 
                                  capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            return result.returncode == 0
        except:
            return False
            
    def get_java_version(self):
        try:
            result = subprocess.run(["java", "-version"], 
                                  capture_output=True, text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            return result.stderr.split()[2].replace('"', '')
        except:
            return "Inconnu"
            
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
        
    def check_for_updates_gui(self):
        try:
            messagebox.showinfo("Vérification", "Vérification des mises à jour en cours...")
            
            has_update, latest_version, download_url = self.update_manager.check_for_updates()
            
            if has_update:
                result = messagebox.askyesno(
                    "Mise à jour disponible",
                    f"Une nouvelle version ({latest_version}) est disponible.\n\n"
                    f"Version actuelle : {self.update_manager.current_version}\n"
                    f"Voulez-vous télécharger et installer la mise à jour ?"
                )
                
                if result and download_url:
                    self.download_and_install_update(download_url, latest_version)
            else:
                messagebox.showinfo("À jour", f"ZSDumper est à jour (version {self.update_manager.current_version})")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la vérification : {str(e)}")
            
    def download_and_install_update(self, download_url, latest_version):
        progress_window = tk.Toplevel(self)
        progress_window.title("Mise à jour")
        progress_window.geometry("480x240")
        progress_window.configure(bg=self.colors['bg'])
        progress_window.resizable(False, False)
        progress_window.transient(self)
        progress_window.grab_set()
        
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (480 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (240 // 2)
        progress_window.geometry(f"+{x}+{y}")
        
        progress_card = tk.Frame(progress_window, bg=self.colors['card'])
        progress_card.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(progress_card, text=f"Téléchargement v{latest_version}...",
                bg=self.colors['card'], fg=self.colors['text'],
                font=("Manrope", 15, "bold")).pack(pady=45)
        
        progress = ttk.Progressbar(progress_card, length=380, mode='determinate')
        progress.pack(pady=25)
        
        def progress_callback(percent):
            progress['value'] = percent
            progress_window.update()
            
        def download_thread():
            try:
                success = self.update_manager.download_update(download_url, progress_callback)
                
                if success:
                    progress_window.destroy()
                    messagebox.showinfo("Téléchargement", "Téléchargement terminé !\nL'installation va démarrer...")
                    self.update_manager.install_update("Temp_Updates/ZSDumper_Update.exe")
                else:
                    progress_window.destroy()
                    messagebox.showerror("Erreur", "Échec du téléchargement")
                    
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Erreur", f"Erreur : {str(e)}")
        
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    app = ZSDumperApp()
    app.mainloop()
