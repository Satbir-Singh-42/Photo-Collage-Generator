#!/usr/bin/env python3
"""
Photo Collage Generator - Graphical User Interface

A desktop-style GUI application similar to Shape Collage for creating 
photo collages with various shapes, sizes, and effects.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import threading
import queue

from collage_generator import CollageGenerator, CollageSettings, CollageShape


class CollageApp:
    """Main GUI Application for Photo Collage Generator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Collage Generator")
        self.root.geometry("950x650")
        self.root.minsize(700, 450)
        
        self.photos = []
        self.photo_thumbnails = {}
        self.preview_image = None
        self.current_collage = None
        self.is_generating = False
        self.selected_indices = set()
        self.custom_mask_path = None
        self.mask_preview_image = None
        
        self.update_queue = queue.Queue()
        
        self.settings = CollageSettings()
        
        self.setup_styles()
        self.setup_menu()
        self.setup_main_layout()
        
        self.resize_after_id = None
        self.root.bind('<Configure>', self.on_window_resize)
        
        self.process_queue()
        
    def process_queue(self):
        """Process UI updates from background threads."""
        try:
            while True:
                callback = self.update_queue.get_nowait()
                callback()
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)
        
    def queue_update(self, callback):
        """Queue a UI update to be processed on the main thread."""
        self.update_queue.put(callback)
        
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TButton', padding=5)
        style.configure('Header.TLabel', font=('Segoe UI', 9, 'bold'))
        style.configure('Upload.TButton', padding=10, font=('Segoe UI', 10, 'bold'))
        style.configure('Action.TButton', padding=8)
        
    def setup_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Upload Photos...", command=self.add_photos)
        file_menu.add_command(label="Upload Folder...", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Save Collage...", command=self.save_collage)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Restore Defaults", command=self.restore_defaults)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_main_layout(self):
        """Create the main three-panel layout with responsive design."""
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        main_frame.columnconfigure(0, weight=2, minsize=160)
        main_frame.columnconfigure(1, weight=3, minsize=250)
        main_frame.columnconfigure(2, weight=2, minsize=220)
        main_frame.rowconfigure(0, weight=1)
        
        self.setup_photos_panel(main_frame)
        self.setup_preview_panel(main_frame)
        self.setup_settings_panel(main_frame)
        
    def on_window_resize(self, event):
        """Handle window resize for responsive layout with debouncing."""
        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
        
        self.resize_after_id = self.root.after(150, self._delayed_resize)
        
    def _delayed_resize(self):
        """Delayed resize handler to prevent excessive redraws."""
        self.resize_after_id = None
        if hasattr(self, 'preview_canvas') and self.current_collage:
            self._display_preview(self.current_collage)
        
    def setup_photos_panel(self, parent):
        """Create the left panel with photo list and upload buttons."""
        photos_frame = ttk.LabelFrame(parent, text="Photos", padding="5")
        photos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        photos_frame.columnconfigure(0, weight=1)
        photos_frame.rowconfigure(1, weight=1)
        
        upload_frame = ttk.Frame(photos_frame)
        upload_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        upload_frame.columnconfigure(0, weight=1)
        upload_frame.columnconfigure(1, weight=1)
        
        upload_btn = ttk.Button(upload_frame, text="Upload Images", 
                               command=self.add_photos, style='Upload.TButton')
        upload_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        folder_btn = ttk.Button(upload_frame, text="Upload Folder", 
                               command=self.add_folder, style='Upload.TButton')
        folder_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        list_container = ttk.Frame(photos_frame)
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        scrollbar_y = ttk.Scrollbar(list_container, orient="vertical")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        
        self.photo_listbox = tk.Listbox(
            list_container, 
            selectmode=tk.EXTENDED,
            bg='white',
            font=('Segoe UI', 9),
            yscrollcommand=scrollbar_y.set,
            activestyle='dotbox'
        )
        self.photo_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.config(command=self.photo_listbox.yview)
        
        button_frame = ttk.Frame(photos_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        button_frame.columnconfigure(2, weight=1)
        
        ttk.Button(button_frame, text="+", width=3, command=self.add_photos).grid(row=0, column=0)
        ttk.Button(button_frame, text="-", width=3, command=self.remove_selected).grid(row=0, column=1, padx=2)
        ttk.Button(button_frame, text="Clear", command=self.clear_photos).grid(row=0, column=2, padx=5, sticky="w")
        
        self.photo_count_label = ttk.Label(button_frame, text="0 Photos")
        self.photo_count_label.grid(row=0, column=3, sticky="e")
        
    def setup_preview_panel(self, parent):
        """Create the center panel with collage preview."""
        preview_frame = ttk.LabelFrame(parent, text="Status", padding="5")
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=3)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        self.status_label = ttk.Label(preview_frame, text="Dimensions: -- x --, # Photos: 0")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg='#e0e0e0', relief='sunken', bd=2)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        
        progress_frame = ttk.Frame(preview_frame)
        progress_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=1, column=0)
        
        button_frame = ttk.Frame(preview_frame)
        button_frame.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        ttk.Button(button_frame, text="Preview", command=self.generate_preview, 
                  style='Action.TButton').grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(button_frame, text="Generate All", command=self.generate_collage,
                  style='Action.TButton').grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(button_frame, text="Save", command=self.save_collage,
                  style='Action.TButton').grid(row=0, column=2, sticky="ew", padx=2)
        
    def setup_settings_panel(self, parent):
        """Create the right panel with settings."""
        settings_frame = ttk.Frame(parent)
        settings_frame.grid(row=0, column=2, sticky="nsew", padx=(3, 0))
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.rowconfigure(0, weight=1)
        
        notebook = ttk.Notebook(settings_frame)
        notebook.grid(row=0, column=0, sticky="nsew")
        
        shape_tab = ttk.Frame(notebook, padding="8")
        notebook.add(shape_tab, text="Shape and Size")
        self.setup_shape_tab(shape_tab)
        
        appearance_tab = ttk.Frame(notebook, padding="8")
        notebook.add(appearance_tab, text="Appearance")
        self.setup_appearance_tab(appearance_tab)
        
        advanced_tab = ttk.Frame(notebook, padding="8")
        notebook.add(advanced_tab, text="Advanced")
        self.setup_advanced_tab(advanced_tab)
        
        ttk.Button(settings_frame, text="Restore to Default", 
                  command=self.restore_defaults).grid(row=1, column=0, pady=8)
        
    def setup_shape_tab(self, parent):
        """Setup the Shape and Size settings tab with custom shape support."""
        parent.columnconfigure(0, weight=1)
        
        shape_frame = ttk.LabelFrame(parent, text="Shape", padding="5")
        shape_frame.pack(fill=tk.X, pady=(0, 8))
        shape_frame.columnconfigure(0, weight=1)
        shape_frame.columnconfigure(1, weight=1)
        
        self.shape_var = tk.StringVar(value="rectangle")
        self.shape_var.trace_add("write", self.on_shape_change)
        
        shapes = [
            ("Rectangle", "rectangle"),
            ("Circle", "circle"),
            ("Heart", "heart"),
            ("Custom", "custom"),
        ]
        
        row = 0
        col = 0
        for text, value in shapes:
            rb = ttk.Radiobutton(shape_frame, text=text, variable=self.shape_var, value=value)
            rb.grid(row=row, column=col, sticky="w", padx=5, pady=2)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        self.custom_shape_frame = ttk.Frame(shape_frame)
        self.custom_shape_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.custom_shape_frame.columnconfigure(0, weight=1)
        
        custom_inner = ttk.Frame(self.custom_shape_frame)
        custom_inner.pack(fill=tk.X)
        
        self.custom_mask_label = ttk.Label(custom_inner, text="No mask selected", 
                                          font=('Segoe UI', 8), foreground='gray')
        self.custom_mask_label.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(custom_inner, text="Browse Mask", 
                  command=self.browse_custom_mask).pack(side=tk.RIGHT)
        
        self.mask_preview_label = ttk.Label(self.custom_shape_frame)
        self.mask_preview_label.pack(pady=(5, 0))
        
        self.custom_shape_frame.grid_remove()
        
        size_frame = ttk.LabelFrame(parent, text="Size", padding="5")
        size_frame.pack(fill=tk.X, pady=(0, 8))
        size_frame.columnconfigure(1, weight=1)
        
        ttk.Label(size_frame, text="Collage size:").grid(row=0, column=0, sticky="w", pady=2)
        
        size_inner = ttk.Frame(size_frame)
        size_inner.grid(row=0, column=1, sticky="w", pady=2)
        
        self.width_var = tk.StringVar(value="3000")
        self.height_var = tk.StringVar(value="3000")
        
        ttk.Entry(size_inner, textvariable=self.width_var, width=6).pack(side=tk.LEFT)
        ttk.Label(size_inner, text=" x ").pack(side=tk.LEFT)
        ttk.Entry(size_inner, textvariable=self.height_var, width=6).pack(side=tk.LEFT)
        ttk.Label(size_inner, text=" px").pack(side=tk.LEFT)
        
        ttk.Label(size_frame, text="# Photos:").grid(row=1, column=0, sticky="w", pady=2)
        
        photos_inner = ttk.Frame(size_frame)
        photos_inner.grid(row=1, column=1, sticky="w", pady=2)
        
        self.photos_per_collage_var = tk.StringVar(value="50")
        ttk.Entry(photos_inner, textvariable=self.photos_per_collage_var, width=6).pack(side=tk.LEFT)
        ttk.Label(photos_inner, text=" per collage").pack(side=tk.LEFT)
        
        spacing_frame = ttk.LabelFrame(parent, text="Photo spacing", padding="5")
        spacing_frame.pack(fill=tk.X)
        spacing_frame.columnconfigure(1, weight=1)
        
        self.spacing_var = tk.IntVar(value=5)
        
        ttk.Label(spacing_frame, text="Spacing:").grid(row=0, column=0, sticky="w")
        ttk.Scale(spacing_frame, from_=0, to=50, variable=self.spacing_var, 
                 orient=tk.HORIZONTAL).grid(row=0, column=1, sticky="ew", padx=5)
        self.spacing_label = ttk.Label(spacing_frame, text="5 px", width=6)
        self.spacing_label.grid(row=0, column=2)
        
        self.spacing_var.trace_add("write", self.update_spacing_label)
        
    def on_shape_change(self, *args):
        """Handle shape selection change."""
        if self.shape_var.get() == "custom":
            self.custom_shape_frame.grid()
        else:
            self.custom_shape_frame.grid_remove()
            
    def browse_custom_mask(self):
        """Browse for a custom PNG mask file."""
        filetypes = [
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(
            title="Select Custom Shape Mask (PNG)",
            filetypes=filetypes
        )
        
        if file_path:
            try:
                img = Image.open(file_path)
                if img.mode != 'RGBA' and img.mode != 'L':
                    img = img.convert('L')
                    
                self.custom_mask_path = file_path
                
                name = Path(file_path).name
                if len(name) > 20:
                    name = name[:17] + "..."
                self.custom_mask_label.config(text=name, foreground='black')
                
                preview = img.copy()
                preview.thumbnail((60, 60))
                self.mask_preview_image = ImageTk.PhotoImage(preview)
                self.mask_preview_label.config(image=self.mask_preview_image)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not load mask: {e}")
                self.custom_mask_path = None
                self.custom_mask_label.config(text="No mask selected", foreground='gray')
        
    def setup_appearance_tab(self, parent):
        """Setup the Appearance settings tab."""
        parent.columnconfigure(0, weight=1)
        
        frame_settings = ttk.LabelFrame(parent, text="Frame", padding="5")
        frame_settings.pack(fill=tk.X, pady=(0, 8))
        frame_settings.columnconfigure(1, weight=1)
        
        ttk.Label(frame_settings, text="Thickness:").grid(row=0, column=0, sticky="w", pady=2)
        
        self.frame_var = tk.IntVar(value=20)
        ttk.Scale(frame_settings, from_=0, to=100, variable=self.frame_var, 
                 orient=tk.HORIZONTAL).grid(row=0, column=1, sticky="ew", padx=5)
        self.frame_label = ttk.Label(frame_settings, text="20 px", width=6)
        self.frame_label.grid(row=0, column=2, pady=2)
        
        self.frame_var.trace_add("write", self.update_frame_label)
        
        effects_frame = ttk.LabelFrame(parent, text="Effects", padding="5")
        effects_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.rounded_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(effects_frame, text="Rounded corners (10px)", 
                       variable=self.rounded_var).pack(anchor="w")
        
        self.shadow_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(effects_frame, text="Drop shadow", 
                       variable=self.shadow_var).pack(anchor="w")
        
        bg_frame = ttk.LabelFrame(parent, text="Background", padding="5")
        bg_frame.pack(fill=tk.X)
        
        self.bg_var = tk.StringVar(value="white")
        ttk.Radiobutton(bg_frame, text="White", variable=self.bg_var, 
                       value="white").pack(anchor="w")
        ttk.Radiobutton(bg_frame, text="Transparent", variable=self.bg_var, 
                       value="transparent").pack(anchor="w")
        
    def setup_advanced_tab(self, parent):
        """Setup the Advanced settings tab."""
        parent.columnconfigure(0, weight=1)
        
        output_frame = ttk.LabelFrame(parent, text="Output", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 8))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="DPI:").grid(row=0, column=0, sticky="w", pady=2)
        self.dpi_var = tk.StringVar(value="300")
        ttk.Entry(output_frame, textvariable=self.dpi_var, width=6).grid(row=0, column=1, sticky="w", pady=2)
        
        self.png_var = tk.BooleanVar(value=True)
        self.jpg_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(output_frame, text="Export PNG", 
                       variable=self.png_var).grid(row=1, column=0, sticky="w", pady=2, columnspan=2)
        ttk.Checkbutton(output_frame, text="Export JPG", 
                       variable=self.jpg_var).grid(row=2, column=0, sticky="w", pady=2, columnspan=2)
        
        folder_frame = ttk.LabelFrame(parent, text="Output Folder", padding="5")
        folder_frame.pack(fill=tk.X)
        folder_frame.columnconfigure(0, weight=1)
        
        self.output_folder_var = tk.StringVar(value="Auto-Generated-Collages")
        ttk.Entry(folder_frame, textvariable=self.output_folder_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(folder_frame, text="...", width=3, 
                  command=self.browse_output).grid(row=0, column=1, padx=(5, 0))
        
    def update_spacing_label(self, *args):
        """Update the spacing label text."""
        self.spacing_label.config(text=f"{self.spacing_var.get()} px")
        
    def update_frame_label(self, *args):
        """Update the frame label text."""
        self.frame_label.config(text=f"{self.frame_var.get()} px")
        
    def add_photos(self):
        """Open file dialog to add photos."""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
            ("All files", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Upload Photos", filetypes=filetypes)
        
        added = 0
        for file_path in files:
            if file_path not in self.photos:
                self.photos.append(file_path)
                name = Path(file_path).name
                self.photo_listbox.insert(tk.END, name)
                added += 1
        
        if added > 0:
            self.update_photo_count()
            self.update_status()
            self.progress_label.config(text=f"Added {added} photo(s)")
        
    def add_folder(self):
        """Open folder dialog to add all photos from a folder."""
        folder = filedialog.askdirectory(title="Select Folder to Upload")
        
        if folder:
            folder_path = Path(folder)
            extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
            
            added = 0
            for file_path in sorted(folder_path.iterdir()):
                if file_path.is_file() and file_path.suffix.lower() in extensions:
                    full_path = str(file_path)
                    if full_path not in self.photos:
                        self.photos.append(full_path)
                        self.photo_listbox.insert(tk.END, file_path.name)
                        added += 1
                    
            self.update_photo_count()
            self.update_status()
            if added > 0:
                self.progress_label.config(text=f"Added {added} photo(s) from folder")
            
    def remove_selected(self):
        """Remove selected photos from the list."""
        selection = self.photo_listbox.curselection()
        
        if not selection:
            messagebox.showinfo("Info", "Please select photos to remove.")
            return
            
        for index in reversed(selection):
            self.photo_listbox.delete(index)
            if index < len(self.photos):
                del self.photos[index]
        
        self.update_photo_count()
        self.update_status()
        self.progress_label.config(text=f"Removed {len(selection)} photo(s)")
            
    def clear_photos(self):
        """Clear all photos from the list."""
        count = len(self.photos)
        self.photos.clear()
        self.photo_thumbnails.clear()
        self.photo_listbox.delete(0, tk.END)
            
        self.update_photo_count()
        self.update_status()
        if count > 0:
            self.progress_label.config(text=f"Cleared {count} photo(s)")
        
    def update_photo_count(self):
        """Update the photo count label."""
        count = len(self.photos)
        self.photo_count_label.config(text=f"{count} Photos")
        
    def update_status(self):
        """Update the status label."""
        width = self.width_var.get()
        height = self.height_var.get()
        count = len(self.photos)
        self.status_label.config(text=f"Dimensions: {width} x {height}, # Photos: {count}")
        
    def get_current_settings(self):
        """Get current settings from GUI."""
        shape_map = {
            "rectangle": CollageShape.RECTANGLE,
            "square": CollageShape.SQUARE,
            "heart": CollageShape.HEART,
            "circle": CollageShape.CIRCLE,
            "custom": CollageShape.CUSTOM,
        }
        
        bg_color = (255, 255, 255, 255) if self.bg_var.get() == "white" else (0, 0, 0, 0)
        
        shape = shape_map.get(self.shape_var.get(), CollageShape.SQUARE)
        
        custom_mask = None
        if shape == CollageShape.CUSTOM and self.custom_mask_path:
            custom_mask = self.custom_mask_path
        
        return CollageSettings(
            canvas_size=(int(self.width_var.get()), int(self.height_var.get())),
            dpi=int(self.dpi_var.get()),
            background_color=bg_color,
            outer_frame_thickness=self.frame_var.get(),
            inner_spacing=self.spacing_var.get(),
            enable_rounded_corners=self.rounded_var.get(),
            enable_drop_shadow=self.shadow_var.get(),
            images_per_collage=int(self.photos_per_collage_var.get()),
            shape=shape,
            custom_mask_path=custom_mask,
        )
        
    def generate_preview(self):
        """Generate a preview of the collage."""
        if not self.photos:
            messagebox.showwarning("No Photos", "Please upload some photos first.")
            return
            
        if self.shape_var.get() == "custom" and not self.custom_mask_path:
            messagebox.showwarning("No Mask", "Please select a custom shape mask PNG file.")
            return
            
        if self.is_generating:
            messagebox.showinfo("Busy", "Already generating. Please wait.")
            return
            
        self.is_generating = True
        self.progress_label.config(text="Generating preview...")
        self.progress_var.set(0)
        
        threading.Thread(target=self._generate_preview_thread, daemon=True).start()
        
    def _generate_preview_thread(self):
        """Generate preview in a separate thread."""
        try:
            settings = self.get_current_settings()
            settings.canvas_size = (800, 800)
            
            generator = CollageGenerator(settings)
            
            num_photos = min(len(self.photos), int(self.photos_per_collage_var.get()))
            photo_paths = [Path(p) for p in self.photos[:num_photos]]
            
            self.queue_update(lambda: self.progress_var.set(30))
            
            collage = generator.create_collage(photo_paths, 1)
            
            self.queue_update(lambda: self.progress_var.set(80))
            
            if collage:
                self.current_collage = collage
                self.queue_update(lambda: self._display_preview(collage))
                
            self.queue_update(lambda: self.progress_var.set(100))
            self.queue_update(lambda: self.progress_label.config(text="Preview ready"))
            
        except Exception as e:
            self.queue_update(lambda: messagebox.showerror("Error", f"Error generating preview: {e}"))
            self.queue_update(lambda: self.progress_label.config(text="Error"))
        finally:
            self.is_generating = False
            
    def _display_preview(self, collage):
        """Display the collage preview on the canvas with responsive sizing."""
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width < 10:
            canvas_width = 300
        if canvas_height < 10:
            canvas_height = 300
            
        img = collage.copy()
        
        max_width = canvas_width - 20
        max_height = canvas_height - 20
        
        img_ratio = img.width / img.height
        canvas_ratio = max_width / max_height
        
        if img_ratio > canvas_ratio:
            new_width = max_width
            new_height = int(max_width / img_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * img_ratio)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        self.preview_image = ImageTk.PhotoImage(img)
        
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=self.preview_image, anchor="center"
        )
        
    def generate_collage(self):
        """Generate full-resolution collages."""
        if not self.photos:
            messagebox.showwarning("No Photos", "Please upload some photos first.")
            return
            
        if self.shape_var.get() == "custom" and not self.custom_mask_path:
            messagebox.showwarning("No Mask", "Please select a custom shape mask PNG file.")
            return
            
        if self.is_generating:
            messagebox.showinfo("Busy", "Already generating. Please wait.")
            return
            
        self.is_generating = True
        self.progress_label.config(text="Generating collages...")
        self.progress_var.set(0)
        
        threading.Thread(target=self._generate_collage_thread, daemon=True).start()
        
    def _generate_collage_thread(self):
        """Generate collages in a separate thread."""
        try:
            settings = self.get_current_settings()
            generator = CollageGenerator(settings)
            
            output_folder = Path(self.output_folder_var.get())
            output_folder.mkdir(exist_ok=True)
            
            photo_paths = [Path(p) for p in self.photos]
            groups = generator.split_into_groups(photo_paths)
            
            total_groups = len(groups)
            successful = 0
            
            for i, group in enumerate(groups, 1):
                self.queue_update(lambda i=i: self.progress_label.config(
                    text=f"Generating collage {i}/{total_groups}..."))
                
                try:
                    collage = generator.create_collage(group, i)
                    
                    if collage:
                        base_name = f"collage_{i:02d}"
                        
                        if self.png_var.get():
                            png_path = output_folder / f"{base_name}.png"
                            collage.save(str(png_path), 'PNG', dpi=(settings.dpi, settings.dpi))
                            
                        if self.jpg_var.get():
                            jpg_path = output_folder / f"{base_name}.jpg"
                            rgb = Image.new('RGB', collage.size, (255, 255, 255))
                            rgb.paste(collage, (0, 0), collage if collage.mode == 'RGBA' else None)
                            rgb.save(str(jpg_path), 'JPEG', quality=95, dpi=(settings.dpi, settings.dpi))
                            
                        successful += 1
                        
                except Exception as e:
                    print(f"Error generating collage {i}: {e}")
                    
                progress = int((i / total_groups) * 100)
                self.queue_update(lambda p=progress: self.progress_var.set(p))
                
            self.queue_update(lambda: self.progress_var.set(100))
            self.queue_update(lambda: self.progress_label.config(
                text=f"Complete! {successful}/{total_groups} collage(s) saved."))
            
            output_path = str(output_folder.absolute())
            self.queue_update(lambda: messagebox.showinfo(
                "Complete", f"Generated {successful} collage(s) in:\n{output_path}"))
            
        except Exception as e:
            self.queue_update(lambda: messagebox.showerror("Error", f"Error generating collages: {e}"))
            self.queue_update(lambda: self.progress_label.config(text="Error"))
            
        finally:
            self.is_generating = False
            
    def save_collage(self):
        """Save a single collage with file dialog."""
        if not self.photos:
            messagebox.showwarning("No Photos", "Please upload some photos first.")
            return
            
        if self.shape_var.get() == "custom" and not self.custom_mask_path:
            messagebox.showwarning("No Mask", "Please select a custom shape mask PNG file.")
            return
            
        filetypes = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.asksaveasfilename(
            title="Save Collage",
            defaultextension=".png",
            filetypes=filetypes,
            initialfile="my_collage"
        )
        
        if not file_path:
            return
            
        self.progress_label.config(text="Saving collage...")
        self.progress_var.set(0)
        
        def save_thread():
            try:
                settings = self.get_current_settings()
                generator = CollageGenerator(settings)
                
                num_photos = min(len(self.photos), int(self.photos_per_collage_var.get()))
                photo_paths = [Path(p) for p in self.photos[:num_photos]]
                
                self.queue_update(lambda: self.progress_var.set(30))
                
                full_collage = generator.create_collage(photo_paths, 1)
                
                self.queue_update(lambda: self.progress_var.set(70))
                
                if full_collage:
                    if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                        rgb = Image.new('RGB', full_collage.size, (255, 255, 255))
                        rgb.paste(full_collage, (0, 0), full_collage if full_collage.mode == 'RGBA' else None)
                        rgb.save(file_path, 'JPEG', quality=95, dpi=(settings.dpi, settings.dpi))
                    else:
                        full_collage.save(file_path, 'PNG', dpi=(settings.dpi, settings.dpi))
                        
                    self.queue_update(lambda: self.progress_var.set(100))
                    self.queue_update(lambda: self.progress_label.config(text="Saved successfully!"))
                    self.queue_update(lambda: messagebox.showinfo("Saved", f"Collage saved to:\n{file_path}"))
                else:
                    self.queue_update(lambda: messagebox.showerror("Error", "Failed to generate collage."))
                    
            except Exception as e:
                self.queue_update(lambda: messagebox.showerror("Error", f"Error saving collage: {e}"))
                self.queue_update(lambda: self.progress_label.config(text="Error"))
                
        threading.Thread(target=save_thread, daemon=True).start()
                
    def browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder_var.set(folder)
            
    def restore_defaults(self):
        """Restore all settings to default values."""
        self.shape_var.set("rectangle")
        self.width_var.set("3000")
        self.height_var.set("3000")
        self.photos_per_collage_var.set("50")
        self.spacing_var.set(5)
        self.frame_var.set(20)
        self.rounded_var.set(True)
        self.shadow_var.set(True)
        self.bg_var.set("white")
        self.dpi_var.set("300")
        self.png_var.set(True)
        self.jpg_var.set(True)
        self.output_folder_var.set("Auto-Generated-Collages")
        self.custom_mask_path = None
        self.custom_mask_label.config(text="No mask selected", foreground='gray')
        self.mask_preview_label.config(image='')
        
        self.update_status()
        self.progress_label.config(text="Settings restored to defaults")
        
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Photo Collage Generator",
            "Photo Collage Generator\n\n"
            "A desktop application for creating beautiful photo collages\n"
            "with various shapes, effects, and layout options.\n\n"
            "Features:\n"
            "- Multiple shapes (Rectangle, Circle, Heart, Custom)\n"
            "- Custom PNG mask support for any shape\n"
            "- Rounded corners and drop shadows\n"
            "- Customizable spacing and frames\n"
            "- PNG and JPG export\n"
            "- Batch processing for large collections"
        )


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = CollageApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
