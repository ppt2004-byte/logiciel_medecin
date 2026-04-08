import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import Database

# Configuration globale de CustomTkinter
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

class MedicalApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Logiciel Médical - Suivi Patient Pro")
        self.geometry("1200x800")
        
        # Couleur de fond principale de l'application (plus douce)
        self.configure(fg_color=("#f4f5f7", "#1a1a1a"))
        
        self.db = Database()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==========================================
        # MENU LATÉRAL (SIDEBAR)
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#ffffff", "#2b2b2b"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Logo / Titre
        self.logo_label = ctk.CTkLabel(self.sidebar, text="🏥 Cabinet\nMédical", font=ctk.CTkFont(size=24, weight="bold"), text_color=("#1f538d", "#ffffff"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40))

        # Boutons de navigation (avec emojis et style épuré)
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="📊 Tableau de Bord", command=self.show_dashboard, 
                                           fg_color="transparent", text_color=("#333333", "#ffffff"),
                                           font=ctk.CTkFont(size=15, weight="bold"), anchor="w", height=40)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_add = ctk.CTkButton(self.sidebar, text="➕ Nouveau Patient", command=self.show_add_patient, 
                                     fg_color="transparent", text_color=("#333333", "#ffffff"),
                                     font=ctk.CTkFont(size=15, weight="bold"), anchor="w", height=40)
        self.btn_add.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_list = ctk.CTkButton(self.sidebar, text="📋 Historique & Export", command=self.show_patient_list, 
                                      fg_color="transparent", text_color=("#333333", "#ffffff"),
                                      font=ctk.CTkFont(size=15, weight="bold"), anchor="w", height=40)
        self.btn_list.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Sélecteur de mode (Thème)
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar, values=["System", "Light", "Dark"], 
                                                             command=self.change_appearance_mode_event,
                                                             font=ctk.CTkFont(size=13))
        self.appearance_mode_optionemenu.grid(row=5, column=0, padx=20, pady=(10, 30))

        # ==========================================
        # ZONES DE CONTENU (FRAMES)
        # ==========================================
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.add_patient_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.patient_list_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.setup_dashboard()
        self.setup_add_patient()
        self.setup_patient_list()

        self.show_dashboard()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        self.apply_treeview_style()
        if self.dashboard_frame.winfo_ismapped():
            self.refresh_dashboard()

    def select_frame_by_name(self, name):
        # Mettre en surbrillance le bouton actif avec une couleur douce
        active_color = ("#e8f0fe", "#3d3d3d")
        self.btn_dashboard.configure(fg_color=active_color if name == "dashboard" else "transparent")
        self.btn_add.configure(fg_color=active_color if name == "add" else "transparent")
        self.btn_list.configure(fg_color=active_color if name == "list" else "transparent")

        # Cacher les frames
        self.dashboard_frame.grid_forget()
        self.add_patient_frame.grid_forget()
        self.patient_list_frame.grid_forget()

        # Afficher le frame sélectionné avec un padding aéré
        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
            self.refresh_dashboard()
        elif name == "add":
            self.add_patient_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        elif name == "list":
            self.patient_list_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
            self.refresh_patient_list()

    def show_dashboard(self):
        self.select_frame_by_name("dashboard")

    def show_add_patient(self):
        self.select_frame_by_name("add")

    def show_patient_list(self):
        self.select_frame_by_name("list")

    # ==========================================
    # VUE : TABLEAU DE BORD
    # ==========================================
    def setup_dashboard(self):
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(1, weight=1)
        
        # En-tête (Design "Carte" blanche/grise)
        header_card = ctk.CTkFrame(self.dashboard_frame, fg_color=("#ffffff", "#2b2b2b"), corner_radius=15)
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 20), ipadx=20, ipady=20)
        
        ctk.CTkLabel(header_card, text="Période :", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=(20, 10), pady=20)
        
        self.filter_var = ctk.StringVar(value="Tout")
        self.filter_menu = ctk.CTkOptionMenu(header_card, values=["Aujourd'hui", "Cette Semaine", "Ce Mois", "Cette Année", "Tout"],
                                             variable=self.filter_var, command=self.refresh_dashboard,
                                             font=ctk.CTkFont(size=14), height=35)
        self.filter_menu.pack(side="left")
        
        btn_add_quick = ctk.CTkButton(header_card, text="➕ Ajout Rapide", command=self.show_add_patient, 
                                      fg_color="#27ae60", hover_color="#2ecc71", font=ctk.CTkFont(size=14, weight="bold"), height=40)
        btn_add_quick.pack(side="right", padx=20)

        btn_db_viewer = ctk.CTkButton(header_card, text="🗄️ Base de Données (Lecture Seule)", command=self.open_database_viewer, 
                                      fg_color="#8e44ad", hover_color="#9b59b6", font=ctk.CTkFont(size=14, weight="bold"), height=40)
        btn_db_viewer.pack(side="right", padx=10)

        self.lbl_total = ctk.CTkLabel(header_card, text="Total Patients : 0", font=ctk.CTkFont(size=28, weight="bold"), text_color="#1f538d")
        self.lbl_total.pack(side="right", padx=30)

        # Zone Graphiques (Design "Carte")
        self.graph_card = ctk.CTkFrame(self.dashboard_frame, fg_color=("#ffffff", "#2b2b2b"), corner_radius=15)
        self.graph_card.grid(row=1, column=0, sticky="nsew")
        
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=(8, 5))
        self.fig.patch.set_facecolor('none') # Transparent pour s'intégrer à la carte
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

        # Tooltip dynamique pour le survol
        self.tooltip = self.fig.text(0, 0, "", visible=False, transform=None, 
                                     ha="center", va="bottom", fontsize=12, fontweight="bold",
                                     bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#1f538d", alpha=0.9),
                                     zorder=100)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def open_database_viewer(self):
        db_win = ctk.CTkToplevel(self)
        db_win.title("Base de Données (Lecture Seule)")
        db_win.geometry("1000x600")
        db_win.transient(self)

        tabview = ctk.CTkTabview(db_win)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        tab_patients = tabview.add("Patients (Actifs)")
        tab_archive = tabview.add("Archive (Historique)")
        
        self._create_readonly_table(tab_patients, self.db.get_raw_patients())
        self._create_readonly_table(tab_archive, self.db.get_raw_archive())

    def _create_readonly_table(self, parent, data):
        if not data:
            ctk.CTkLabel(parent, text="Aucune donnée.", font=ctk.CTkFont(size=14)).pack(pady=20)
            return

        columns = list(data[0].keys())
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            # Ajuster la largeur de la colonne en fonction du nom de la colonne
            tree.column(col, anchor='center', width=120)

        scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)
        
        for row in data:
            tree.insert("", "end", values=[row[col] for col in columns])

    def on_hover(self, event):
        if event.inaxes != self.ax1:
            if getattr(self, 'hovered_mp', None) is not None:
                self.hovered_mp = None
                self.draw_pie(None)
                self.tooltip.set_visible(False)
            return

        found_mp = None
        hovered_text = ""
        
        if hasattr(self, 'ax1_wedges'):
            for i, wedge in enumerate(self.ax1_wedges):
                cont, _ = wedge.contains(event)
                if cont:
                    found_mp = self.wedge_to_mp[i]
                    hovered_text = self.ax1_hover_texts[i]
                    break

        if found_mp != getattr(self, 'hovered_mp', None):
            self.hovered_mp = found_mp
            self.draw_pie(found_mp)
            
        if found_mp is not None:
            self.tooltip.set_text(hovered_text)
            self.tooltip.set_position((event.x, event.y + 15))
            self.tooltip.set_visible(True)
        else:
            self.tooltip.set_visible(False)
            
        self.canvas.draw_idle()

    def refresh_dashboard(self, *args):
        periode = self.filter_var.get()
        total, stats_type, stats_paiement = self.db.get_stats(periode)
        self.paiement_details = self.db.get_paiement_details(periode)
        self.stats_paiement = stats_paiement
        
        self.lbl_total.configure(text=f"Total Patients : {total}")
        self.hovered_mp = None
        self.draw_pie(None)

    def draw_pie(self, hovered_mp):
        self.ax1.clear()
        self.ax1.set_facecolor('none')
        self.ax1.axis('equal') # Pour que le pie chart soit bien rond
        
        text_color = "white" if ctk.get_appearance_mode() == "Dark" else "#333333"
            
        if self.stats_paiement:
            main_labels = [str(s["_id"]) for s in self.stats_paiement]
            main_sizes = [s["count"] for s in self.stats_paiement]
            
            palette_p = ['#FF5733', '#3498DB', '#2ECC71', '#F1C40F', '#9B59B6', '#E67E22', '#E74C3C', '#1ABC9C']
            sub_palette = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c4e17f']
            
            draw_sizes = []
            draw_colors = []
            explodes = []
            self.wedge_to_mp = []
            self.ax1_hover_texts = []
            
            for i, mp in enumerate(main_labels):
                color = palette_p[i % len(palette_p)]
                if mp == hovered_mp:
                    # Diviser la part en sous-types
                    details = [d for d in self.paiement_details if d['moyen_paiement'] == mp]
                    for j, d in enumerate(details):
                        draw_sizes.append(d['count'])
                        # Couleurs différentes pour les sous-types
                        draw_colors.append(sub_palette[j % len(sub_palette)])
                        self.wedge_to_mp.append(mp)
                        self.ax1_hover_texts.append(f"💳 {mp}\n• {d['type_patient']}: {d['count']}")
                        explodes.append(0.1) # Effet de zoom
                else:
                    # Garder la part entière
                    draw_sizes.append(main_sizes[i])
                    draw_colors.append(color)
                    self.wedge_to_mp.append(mp)
                    explodes.append(0.0)
                    
                    # Tooltip global pour cette part
                    details = [d for d in self.paiement_details if d['moyen_paiement'] == mp]
                    text = f"💳 {mp} ({main_sizes[i]})\n" + "-" * 20 + "\n"
                    for d in details:
                        text += f"• {d['type_patient']}: {d['count']}\n"
                    self.ax1_hover_texts.append(text.strip())

            self.ax1_wedges, _ = self.ax1.pie(draw_sizes, explode=explodes, colors=draw_colors, startangle=90,
                                              wedgeprops=dict(width=0.4, edgecolor='w'))
            
            # Ajouter une légende pour les moyens de paiement principaux
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=f"{mp} ({main_sizes[i]})", 
                                          markerfacecolor=palette_p[i % len(palette_p)], markersize=10) 
                               for i, mp in enumerate(main_labels)]
            self.ax1.legend(handles=legend_elements, title="Moyens de Paiement", 
                            loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), 
                            frameon=False, labelcolor=text_color)

            self.ax1.set_title("Moyens de Paiement (Survolez pour voir les motifs)", color=text_color, fontweight='bold', pad=20, fontsize=14)
        else:
            self.ax1.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center', color=text_color, fontsize=12)
            self.ax1.set_title("Moyens de Paiement", color=text_color, fontweight='bold', fontsize=14)
            self.ax1.axis('off')
            self.ax1_wedges = []
            self.wedge_to_mp = []
            self.ax1_hover_texts = []

        self.fig.tight_layout()
        self.canvas.draw_idle()

    # ==========================================
    # VUE : AJOUTER PATIENT
    # ==========================================
    def setup_add_patient(self):
        title = ctk.CTkLabel(self.add_patient_frame, text="Créer une nouvelle fiche patient", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(0, 30), anchor="w")

        # Formulaire dans une "Carte"
        form_card = ctk.CTkFrame(self.add_patient_frame, fg_color=("#ffffff", "#2b2b2b"), corner_radius=15)
        form_card.pack(fill="x", ipadx=30, ipady=30)
        form_card.grid_columnconfigure(0, weight=1)
        form_card.grid_columnconfigure(1, weight=2)

        font_label = ctk.CTkFont(size=15, weight="bold")
        font_input = ctk.CTkFont(size=15)

        # Nom
        ctk.CTkLabel(form_card, text="👤 Nom du patient :", font=font_label).grid(row=0, column=0, padx=20, pady=20, sticky="e")
        self.entry_nom = ctk.CTkEntry(form_card, width=350, height=45, font=font_input, corner_radius=8)
        self.entry_nom.grid(row=0, column=1, padx=20, pady=20, sticky="w")

        # Prénom
        ctk.CTkLabel(form_card, text="👤 Prénom :", font=font_label).grid(row=1, column=0, padx=20, pady=20, sticky="e")
        self.entry_prenom = ctk.CTkEntry(form_card, width=350, height=45, font=font_input, corner_radius=8)
        self.entry_prenom.grid(row=1, column=1, padx=20, pady=20, sticky="w")

        # Type Patient
        ctk.CTkLabel(form_card, text="🩺 Motif de la visite :", font=font_label).grid(row=2, column=0, padx=20, pady=20, sticky="e")
        self.combo_type = ctk.CTkComboBox(form_card, values=["Nouveau", "Suivi régulier", "Urgence", "Consultation spécifique", "Autre"], 
                                          width=350, height=45, font=font_input, corner_radius=8)
        self.combo_type.grid(row=2, column=1, padx=20, pady=20, sticky="w")

        # Paiement
        ctk.CTkLabel(form_card, text="💳 Moyen de paiement :", font=font_label).grid(row=3, column=0, padx=20, pady=20, sticky="e")
        self.combo_paiement = ctk.CTkComboBox(form_card, values=["Carte Bancaire", "Espèces", "Chèque", "Tiers Payant"], 
                                              width=350, height=45, font=font_input, corner_radius=8)
        self.combo_paiement.grid(row=3, column=1, padx=20, pady=20, sticky="w")

        # Bouton Enregistrer (plus gros, plus beau)
        btn_save = ctk.CTkButton(form_card, text="💾 Enregistrer le dossier", command=self.save_patient, 
                                 width=300, height=55, font=ctk.CTkFont(size=18, weight="bold"), corner_radius=10)
        btn_save.grid(row=4, column=0, columnspan=2, pady=(40, 10))

    def save_patient(self):
        nom = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        t_patient = self.combo_type.get()
        m_paiement = self.combo_paiement.get()

        if not nom or not prenom:
            messagebox.showwarning("Erreur de saisie", "Veuillez remplir le nom et le prénom.")
            return

        self.db.add_patient(nom.upper(), prenom.capitalize(), t_patient, m_paiement)
        messagebox.showinfo("Succès", f"Le dossier de {prenom.capitalize()} {nom.upper()} a été créé avec succès.")
        
        self.entry_nom.delete(0, 'end')
        self.entry_prenom.delete(0, 'end')
        self.show_dashboard()

    # ==========================================
    # VUE : LISTE ET EXPORT
    # ==========================================
    def setup_patient_list(self):
        title = ctk.CTkLabel(self.patient_list_frame, text="Historique des consultations", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(0, 20), anchor="w")

        # En-tête (Carte)
        header_card = ctk.CTkFrame(self.patient_list_frame, fg_color=("#ffffff", "#2b2b2b"), corner_radius=15)
        header_card.pack(fill="x", pady=(0, 20), ipadx=20, ipady=15)
        
        ctk.CTkLabel(header_card, text="Filtrer par :", font=ctk.CTkFont(size=15, weight="bold")).pack(side="left", padx=(20, 10))

        self.list_filter_var = ctk.StringVar(value="Tout")
        self.list_filter_menu = ctk.CTkOptionMenu(header_card, values=["Aujourd'hui", "Cette Semaine", "Ce Mois", "Cette Année", "Tout"],
                                             variable=self.list_filter_var, command=self.refresh_patient_list, font=ctk.CTkFont(size=14))
        self.list_filter_menu.pack(side="left")

        btn_export = ctk.CTkButton(header_card, text="📥 Exporter (Excel)", command=self.export_excel, 
                                   fg_color="#27ae60", hover_color="#2ecc71", font=ctk.CTkFont(size=14, weight="bold"), height=35)
        btn_export.pack(side="right", padx=20)

        # Tableau (Carte)
        self.tree_card = ctk.CTkFrame(self.patient_list_frame, fg_color=("#ffffff", "#2b2b2b"), corner_radius=15)
        self.tree_card.pack(fill="both", expand=True, ipadx=10, ipady=10)
        
        self.apply_treeview_style()

        columns = ("Nom", "Prénom", "Type", "Paiement", "Date")
        self.tree = ttk.Treeview(self.tree_card, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center', width=150 if col != "Date" else 200)

        scrollbar = ttk.Scrollbar(self.tree_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=20)

        # Actions
        action_frame = ctk.CTkFrame(self.patient_list_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=(20, 0))
        
        btn_edit = ctk.CTkButton(action_frame, text="✏️ Modifier la fiche", command=self.edit_patient, font=ctk.CTkFont(weight="bold"), height=40)
        btn_edit.pack(side="left", padx=(0, 15))
        
        btn_delete = ctk.CTkButton(action_frame, text="🗑️ Supprimer", command=self.delete_patient, fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(weight="bold"), height=40)
        btn_delete.pack(side="left")

    def apply_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            bg_color = "#2b2b2b"
            fg_color = "white"
            header_bg = "#1f538d"
            selected_bg = "#3a7ebf"
        else:
            bg_color = "#ffffff"
            fg_color = "#333333"
            header_bg = "#3498db"
            selected_bg = "#d6eaf8"

        style.configure("Treeview", 
                        background=bg_color, 
                        fieldbackground=bg_color, 
                        foreground=fg_color,
                        rowheight=40, # Lignes beaucoup plus hautes et aérées
                        bordercolor=bg_color,
                        borderwidth=0,
                        font=('Helvetica', 12))
        
        # Style spécifique pour la sélection en mode clair (texte noir sur fond bleu clair)
        if mode == "Light":
            style.map("Treeview", background=[("selected", selected_bg)], foreground=[("selected", "black")])
        else:
            style.map("Treeview", background=[("selected", selected_bg)])

        style.configure("Treeview.Heading", 
                        background=header_bg, 
                        foreground="white", 
                        font=('Helvetica', 13, 'bold'),
                        borderwidth=0,
                        padding=(0, 10))

    def refresh_patient_list(self, *args):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        periode = self.list_filter_var.get()
        patients = self.db.get_patients(periode)
        
        for p in patients:
            date_str = p["date_enregistrement"].strftime("%d/%m/%Y %H:%M")
            self.tree.insert("", "end", iid=p["id"], values=(p["nom"], p["prenom"], p["type_patient"], p["moyen_paiement"], date_str))

    def edit_patient(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un patient dans la liste pour le modifier.")
            return
            
        values = self.tree.item(selected_item, "values")
        
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Modifier Patient")
        edit_win.geometry("550x500")
        edit_win.grab_set() 
        edit_win.transient(self) 
        
        ctk.CTkLabel(edit_win, text="✏️ Édition du dossier", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 20))
        
        form_frame = ctk.CTkFrame(edit_win, fg_color=("#ffffff", "#2b2b2b"), corner_radius=15)
        form_frame.pack(pady=10, padx=30, fill="both", expand=True, ipadx=10, ipady=10)
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=2)
        
        font_label = ctk.CTkFont(size=14, weight="bold")

        ctk.CTkLabel(form_frame, text="Nom :", font=font_label).grid(row=0, column=0, padx=15, pady=15, sticky="e")
        entry_nom = ctk.CTkEntry(form_frame, height=35)
        entry_nom.grid(row=0, column=1, padx=15, pady=15, sticky="we")
        entry_nom.insert(0, values[0])
        
        ctk.CTkLabel(form_frame, text="Prénom :", font=font_label).grid(row=1, column=0, padx=15, pady=15, sticky="e")
        entry_prenom = ctk.CTkEntry(form_frame, height=35)
        entry_prenom.grid(row=1, column=1, padx=15, pady=15, sticky="we")
        entry_prenom.insert(0, values[1])
        
        ctk.CTkLabel(form_frame, text="Type :", font=font_label).grid(row=2, column=0, padx=15, pady=15, sticky="e")
        combo_type = ctk.CTkComboBox(form_frame, values=["Nouveau", "Suivi régulier", "Urgence", "Consultation spécifique", "Autre"], height=35)
        combo_type.grid(row=2, column=1, padx=15, pady=15, sticky="we")
        combo_type.set(values[2])
        
        ctk.CTkLabel(form_frame, text="Paiement :", font=font_label).grid(row=3, column=0, padx=15, pady=15, sticky="e")
        combo_paiement = ctk.CTkComboBox(form_frame, values=["Carte Bancaire", "Espèces", "Chèque", "Tiers Payant"], height=35)
        combo_paiement.grid(row=3, column=1, padx=15, pady=15, sticky="we")
        combo_paiement.set(values[3])
        
        def save_edit():
            n = entry_nom.get().strip()
            p = entry_prenom.get().strip()
            t = combo_type.get()
            m = combo_paiement.get()
            
            if not n or not p:
                messagebox.showwarning("Erreur", "Nom et prénom obligatoires.", parent=edit_win)
                return
                
            self.db.update_patient(selected_item, n.upper(), p.capitalize(), t, m)
            self.refresh_patient_list()
            if self.dashboard_frame.winfo_ismapped():
                self.refresh_dashboard()
            edit_win.destroy()
            messagebox.showinfo("Succès", "Les informations ont été mises à jour.")
            
        ctk.CTkButton(edit_win, text="💾 Enregistrer les modifications", command=save_edit, font=ctk.CTkFont(size=15, weight="bold"), height=45).pack(pady=20)

    def delete_patient(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un patient dans la liste pour le supprimer.")
            return
            
        values = self.tree.item(selected_item, "values")
        patient_name = f"{values[1]} {values[0]}"
        
        if messagebox.askyesno("Confirmation de suppression", f"Êtes-vous sûr de vouloir supprimer définitivement le dossier de : {patient_name} ?\n\nCette action est irréversible."):
            self.db.delete_patient(selected_item)
            self.refresh_patient_list()
            if self.dashboard_frame.winfo_ismapped():
                self.refresh_dashboard()
            messagebox.showinfo("Succès", f"Le dossier de {patient_name} a été supprimé.")

    def export_excel(self):
        periode = self.list_filter_var.get()
        patients = self.db.get_patients(periode)
        
        if not patients:
            messagebox.showinfo("Export Excel", "Aucune donnée à exporter pour cette période.")
            return

        default_filename = f"Export_Patients_{periode.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                initialfile=default_filename,
                                                filetypes=[("Fichiers Excel", "*.xlsx")],
                                                title="Sauvegarder l'export Excel")
        if not filepath:
            return

        data = []
        for p in patients:
            data.append({
                "Nom": p["nom"],
                "Prénom": p["prenom"],
                "Motif": p["type_patient"],
                "Paiement": p["moyen_paiement"],
                "Date": p["date_enregistrement"].strftime("%Y-%m-%d %H:%M:%S")
            })

        df = pd.DataFrame(data)
        try:
            df.to_excel(filepath, index=False, engine='openpyxl')
            messagebox.showinfo("Succès", f"Fichier Excel exporté avec succès !\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export Excel:\n{str(e)}")

if __name__ == "__main__":
    app = MedicalApp()
    app.mainloop()