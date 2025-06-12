#!/usr/bin/env python3
"""
Ollama Vision Model Analyzer

A modern GUI application for analyzing images with any Ollama vision model.
No more command line nonsense!

Requirements:
- pip install ollama pillow
- Ollama running locally with any vision model
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import ollama
import base64
import os
import threading
from PIL import Image, ImageTk

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class VisionModelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Vision Model Analyzer")
        self.root.geometry("600x700")  # Reduced width by 50 pixels
        self.root.configure(bg='#f0f0f0')
        
        # Initialize Ollama client - try different connection methods
        self.client = None
        self.selected_image_path = None
        self.model_names = []  # Store actual model names separately from display names
        self.successful_connection = None  # Store successful connection parameters
        
        self.setup_ui()
        self.setup_drag_and_drop()
        self.initialize_ollama_client()
        
    def setup_ui(self):
        """Create the user interface"""
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main container frame
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Create a canvas and scrollbar for scrolling
        canvas = tk.Canvas(container, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Main content frame
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for main frame
        main_frame.columnconfigure(1, weight=1)
        
        # Bind canvas resize to adjust window width
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas_width)
        
        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', bind_mousewheel)
        canvas.bind('<Leave>', unbind_mousewheel)
        
        # Title
        title_label = ttk.Label(main_frame, text="🖼️ Ollama Vision Model Analyzer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Model selection
        ttk.Label(main_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, 
                                       state="readonly", width=30)
        self.model_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Refresh models button
        refresh_btn = ttk.Button(main_frame, text="🔄", command=self.refresh_connection, width=3)
        refresh_btn.grid(row=1, column=2, pady=5, padx=(5, 0))
        
        # Image selection
        ttk.Label(main_frame, text="Image:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        image_frame.columnconfigure(0, weight=1)
        
        self.image_path_var = tk.StringVar(value="No image selected")
        self.image_label = ttk.Label(image_frame, textvariable=self.image_path_var, 
                                    foreground="gray")
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(image_frame, text="Browse...", command=self.browse_image)
        browse_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Image preview
        preview_title = "Image Preview (drag & drop here)" if DND_AVAILABLE else "Image Preview"
        self.preview_frame = ttk.LabelFrame(main_frame, text=preview_title, padding="10")
        self.preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        self.preview_frame.columnconfigure(0, weight=1)
        
        preview_text = "No image selected\nDrag & drop an image here or use Browse..." if DND_AVAILABLE else "No image selected\nUse Browse... to select an image"
        self.preview_label = ttk.Label(self.preview_frame, text=preview_text, 
                                      foreground="gray", justify="center")
        self.preview_label.grid(row=0, column=0)
        
        # Prompt input
        ttk.Label(main_frame, text="Prompt:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=5)
        
        self.prompt_text = scrolledtext.ScrolledText(main_frame, height=4, width=50)
        self.prompt_text.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), 
                             pady=5, padx=(10, 0))
        self.prompt_text.insert(tk.END, "Describe what you see in this image.")
        
        # Analyze button
        self.analyze_btn = ttk.Button(main_frame, text="🔍 Analyze Image", 
                                     command=self.analyze_image_threaded, 
                                     style="Accent.TButton")
        self.analyze_btn.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Response area
        response_frame = ttk.LabelFrame(main_frame, text="Model Response", padding="10")
        response_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.response_text = scrolledtext.ScrolledText(response_frame, height=10, width=70,
                                                      wrap=tk.WORD, font=('Arial', 10))
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Copy response button
        copy_btn = ttk.Button(response_frame, text="📋 Copy Response", 
                             command=self.copy_response)
        copy_btn.grid(row=1, column=0, pady=(10, 0))
    
    def setup_drag_and_drop(self):
        """Setup drag and drop functionality for image files"""
        if not DND_AVAILABLE:
            # Update preview text to indicate drag and drop is not available
            self.preview_label.configure(text="No image selected\nUse Browse... to select an image")
            return
        
        def drop_enter(event):
            self.preview_frame.configure(relief="solid")
            return "copy"
        
        def drop_leave(event):
            self.preview_frame.configure(relief="groove")
            return "copy"
        
        def drop(event):
            self.preview_frame.configure(relief="groove")
            
            # Get the dropped files
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0]
                
                # Check if it's an image file
                valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
                if file_path.lower().endswith(valid_extensions):
                    self.selected_image_path = file_path
                    display_name = os.path.basename(file_path)
                    self.image_path_var.set(display_name)
                    self.image_label.configure(foreground="black")
                    self.show_image_preview(file_path)
                else:
                    messagebox.showerror("Invalid File", 
                                       "Please drop a valid image file (JPG, PNG, GIF, BMP, TIFF)")
            return "copy"
        
        # Enable drag and drop
        self.preview_frame.drop_target_register(DND_FILES)
        self.preview_frame.dnd_bind("<<DropEnter>>", drop_enter)
        self.preview_frame.dnd_bind("<<DropLeave>>", drop_leave)
        self.preview_frame.dnd_bind("<<Drop>>", drop)
        
        # Also enable on the preview label
        self.preview_label.drop_target_register(DND_FILES)
        self.preview_label.dnd_bind("<<DropEnter>>", drop_enter)
        self.preview_label.dnd_bind("<<DropLeave>>", drop_leave)
        self.preview_label.dnd_bind("<<Drop>>", drop)
    
    def initialize_ollama_client(self):
        """Initialize Ollama client with different connection attempts"""
        connection_attempts = [
            ("http://localhost:11434", "Default port 11434"),
            ("http://127.0.0.1:11434", "Localhost IP with port 11434"),
            ("http://localhost:8080", "Alternative port 8080"),
            (None, "Default client configuration")
        ]
        
        for host, description in connection_attempts:
            try:
                if host:
                    self.client = ollama.Client(host=host)
                else:
                    self.client = ollama.Client()
                
                # Test the connection by trying to list models
                models = self.client.list()
                self.successful_connection = host  # Store successful connection
                self.update_status(f"✅ Connected via {description}")
                self.load_available_models()
                return
                
            except Exception as e:
                self.update_status(f"❌ Failed {description}: {str(e)[:50]}...")
                continue
        
        # If all attempts failed
        self.client = None
        self.successful_connection = None
        error_msg = ("Could not connect to Ollama server.\n\n"
                    "Troubleshooting:\n"
                    "1. Make sure 'ollama serve' is running\n"
                    "2. Try restarting Ollama\n"
                    "3. Check if another app is using port 11434\n"
                    "4. Try running: ollama list (in command line)")
        
        messagebox.showerror("Connection Failed", error_msg)
        self.update_status("❌ No connection to Ollama")
        
    def load_available_models(self):
        """Load all available models from Ollama"""
        if not self.client:
            self.update_status("❌ No Ollama connection")
            return
            
        try:
            models_response = self.client.list()
            
            # Get all models - let user choose
            all_models = []
            vision_indicators = ['llava', 'vision', 'vi', 'clip', 'moondream', 'qwen2.5vi', 'bakllava']
            
            # Handle different possible response structures
            if isinstance(models_response, dict):
                models_list = models_response.get('models', [])
            elif hasattr(models_response, 'models'):
                models_list = models_response.models
            else:
                models_list = models_response
            
            for model in models_list:
                try:
                    # Extract just the model name string
                    if hasattr(model, 'model'):
                        model_name = model.model  # For model objects
                    elif isinstance(model, dict):
                        model_name = model.get('name') or model.get('model')
                    else:
                        model_name = str(model)
                    
                    if model_name:
                        # Check if it's likely a vision model for sorting
                        is_vision = any(indicator in model_name.lower() for indicator in vision_indicators)
                        
                        all_models.append({
                            'name': model_name,
                            'is_vision': is_vision
                        })
                            
                except Exception as model_error:
                    print(f"DEBUG - Error processing model: {model}, Error: {model_error}")
                    continue
            
            # Sort models with vision models first
            all_models.sort(key=lambda x: (not x['is_vision'], x['name']))
            
            # Set up the dropdown with plain model names
            model_names = [model['name'] for model in all_models]
            self.model_names = model_names  # Store actual names
            
            self.model_combo['values'] = model_names
            
            if all_models:
                # Select first vision model if available, otherwise first model
                vision_models = [i for i, model in enumerate(all_models) if model['is_vision']]
                selected_index = vision_models[0] if vision_models else 0
                self.model_combo.set(model_names[selected_index])
                
                total_count = len(all_models)
                self.update_status(f"✅ Found {total_count} model(s)")
            else:
                self.update_status("❌ No models found")
                messagebox.showwarning("No Models", 
                                     "No models found in Ollama.\n\n"
                                     "Install a model with:\n"
                                     "ollama pull llava:7b\n"
                                     "ollama pull qwen2.5-coder:7b\n"
                                     "ollama pull moondream")
                
        except Exception as e:
            self.update_status(f"❌ Error loading models: {e}")
            print(f"DEBUG - Full error: {e}")
            
            messagebox.showerror("Model Loading Error", 
                               f"Could not load models: {e}\n\n"
                               f"Try clicking the refresh button (🔄) or restart the application.")
    
    def refresh_connection(self):
        """Refresh the Ollama connection and reload models"""
        self.update_status("🔄 Refreshing connection...")
        
        # If we have a known successful connection, try that first
        if self.successful_connection:
            try:
                if self.successful_connection:
                    self.client = ollama.Client(host=self.successful_connection)
                else:
                    self.client = ollama.Client()
                
                # Test the connection
                models = self.client.list()
                self.update_status("✅ Reconnected successfully")
                self.load_available_models()
                return
                
            except Exception as e:
                self.update_status(f"❌ Previous connection failed, trying all methods...")
        
        # If previous connection failed or we don't have one, try all methods
        self.initialize_ollama_client()
    
    def browse_image(self):
        """Open file dialog to select an image"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=file_types
        )
        
        if filename:
            self.selected_image_path = filename
            # Show just the filename, not the full path
            display_name = os.path.basename(filename)
            self.image_path_var.set(display_name)
            self.image_label.configure(foreground="black")
            self.show_image_preview(filename)
    
    def show_image_preview(self, image_path):
        """Show a preview of the selected image"""
        try:
            # Open and resize image for preview
            image = Image.open(image_path)
            
            # Calculate size to fit in preview area (max 150x150 to save space)
            image.thumbnail((150, 150), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update preview label
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.preview_label.configure(image="", text=f"Preview error: {e}")
    
    def analyze_image_threaded(self):
        """Run image analysis in a separate thread to avoid freezing the GUI"""
        threading.Thread(target=self.analyze_image, daemon=True).start()
    
    def analyze_image(self):
        """Analyze the selected image with the prompt"""
        # Check connection first
        if not self.client:
            messagebox.showerror("No Connection", 
                               "Not connected to Ollama server.\n"
                               "Click the refresh button (🔄) to reconnect.")
            return
            
        # Validation
        if not self.selected_image_path:
            messagebox.showerror("No Image", "Please select an image first.")
            return
        
        if not self.model_var.get():
            messagebox.showerror("No Model", "Please select a vision model.")
            return
        
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showerror("No Prompt", "Please enter a prompt.")
            return
        
        # Show progress
        self.progress.start()
        self.analyze_btn.configure(state="disabled", text="🔍 Analyzing...")
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, "Analyzing image, please wait...")
        
        try:
            # Encode image to base64
            with open(self.selected_image_path, 'rb') as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Get the selected model name directly
            selected_model = self.model_var.get().strip()
            
            print(f"DEBUG - Using model: '{selected_model}' (type: {type(selected_model)})")
            
            # Send to vision model
            response = self.client.generate(
                model=selected_model,
                prompt=prompt,
                images=[image_base64],
                stream=False
            )
            
            # Update UI with response
            self.root.after(0, self.display_response, response['response'])
            
        except Exception as e:
            print(f"DEBUG - Analysis error: {e}")
            self.root.after(0, self.display_error, str(e))
        
        finally:
            # Hide progress and re-enable button
            self.root.after(0, self.analysis_complete)
    
    def display_response(self, response):
        """Display the model's response"""
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, response)
        self.update_status("✅ Analysis complete!")
    
    def display_error(self, error_msg):
        """Display an error message"""
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, f"❌ Error: {error_msg}")
        self.update_status("❌ Analysis failed")
    
    def analysis_complete(self):
        """Reset UI after analysis is complete"""
        self.progress.stop()
        self.analyze_btn.configure(state="normal", text="🔍 Analyze Image")
    
    def copy_response(self):
        """Copy the response to clipboard"""
        response = self.response_text.get(1.0, tk.END).strip()
        if response:
            self.root.clipboard_clear()
            self.root.clipboard_append(response)
            self.update_status("📋 Response copied to clipboard!")
    
    def update_status(self, message):
        """Update the window title with status message"""
        self.root.title(f"Ollama Vision Model Analyzer - {message}")


def main():
    """Main function to run the GUI application"""
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    # Set up modern theme if available
    try:
        style = ttk.Style()
        style.theme_use('clam')  # Modern looking theme
    except:
        pass
    
    app = VisionModelGUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
