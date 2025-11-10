import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import openpyxl
import json
import os
from pathlib import Path
import threading
import re

class AuditorAppUniversal:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Auditor Data Cleaner - by Rashid Zainol")
        self.root.geometry("1100x900")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.file_path = None
        self.df = None
        self.processed_data = []
        self.config_file = "auditor_config_universal.json"
        
        # Default configuration
        self.config = {
            "col_date": "A",
            "col_journal": "C", 
            "col_reference": "G",
            "col_description": "I",
            "col_debit": "W",
            "col_credit": "auto",
            "col_balance_start": "AF",
            "col_balance_end": "AF",
            "col_account_code": "E",
            "col_account_name": "K",
            "running_credit_mode": "auto",
            "debit_type": "auto",
            "credit_type": "auto", 
            "balance_type": "auto"
        }
        
        self.load_config()
        self.create_widgets()
        self.create_credit_section()
    
    def create_credit_section(self):
        """Create credit section at the bottom"""
        # Credit frame at the very bottom
        credit_frame = ttk.Frame(self.root, padding="5")
        credit_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Separator line
        separator = ttk.Separator(credit_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 5))
        
        # Credit text - Universal version
        credit_text = "© 2025 Universal Auditor Tools | Developed by Rashid Zainol | JANN Sarawak"
        
        credit_label = ttk.Label(credit_frame, text=credit_text, 
                                foreground='#2c3e50', 
                                font=('Arial', 9, 'bold'),
                                justify=tk.CENTER,
                                background='#ecf0f1',
                                relief='solid',
                                borderwidth=1,
                                padding=8)
        credit_label.pack(fill=tk.X)
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except:
                pass
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title - Universal version
        title_label = ttk.Label(main_frame, text="📊 UNIVERSAL AUDITOR DATA CLEANER", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="1. SELECT EXCEL FILE", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_inner_frame = ttk.Frame(file_frame)
        file_inner_frame.pack(fill=tk.X)
        
        ttk.Button(file_inner_frame, text="Browse Excel File", 
                  command=self.browse_file).pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_label = ttk.Label(file_inner_frame, text="No file selected", 
                                   background='#e8e8e8', padding="5", width=80)
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Configuration panel
        config_frame = ttk.LabelFrame(main_frame, text="2. CONFIGURE COLUMNS (Use Excel Letters: A, B, C, AA, AB...)", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_config_controls(config_frame)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="PROCESS FILE", 
                  command=self.process_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Auto-Detect Columns", 
                  command=self.auto_detect).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Save Config", 
                  command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Reset Config", 
                  command=self.reset_config).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Diagnostic info
        diag_frame = ttk.LabelFrame(main_frame, text="PROCESSING LOG", padding="5")
        diag_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.diagnostic_text = scrolledtext.ScrolledText(diag_frame, height=6, width=100)
        self.diagnostic_text.pack(fill=tk.BOTH, expand=True)
        
        # Export buttons (initially hidden)
        export_frame = ttk.LabelFrame(main_frame, text="3. EXPORT RESULTS", padding="10")
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        export_inner = ttk.Frame(export_frame)
        export_inner.pack()
        
        self.export_csv_btn = ttk.Button(export_inner, text="📥 EXPORT AS CSV", 
                                        command=self.export_csv, state=tk.DISABLED)
        self.export_csv_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_excel_btn = ttk.Button(export_inner, text="📥 EXPORT AS EXCEL", 
                                          command=self.export_excel, state=tk.DISABLED)
        self.export_excel_btn.pack(side=tk.LEFT)
        
        # Instructions
        instructions = ttk.Label(export_frame, text="💡 After processing, click above to save your cleaned data to a file", 
                                foreground='blue', font=('Arial', 9))
        instructions.pack(pady=(5, 0))
        
        # Results table
        table_frame = ttk.LabelFrame(main_frame, text="PROCESSED DATA PREVIEW (With Account Codes & Names)", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for results
        columns = ('Account Code', 'Account Name', 'Date', 'Journal', 'Reference', 
                  'Description', 'Debit', 'Credit', 'Balance')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Define headings
        column_widths = {
            'Account Code': 100,
            'Account Name': 150, 
            'Date': 100,
            'Journal': 80,
            'Reference': 120,
            'Description': 200,
            'Debit': 80,
            'Credit': 80,
            'Balance': 80
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

    def create_config_controls(self, parent):
        """Create configuration controls"""
        # Create a grid layout
        for i in range(6):
            parent.columnconfigure(i, weight=1)
        
        # Row 0 - Basic columns
        ttk.Label(parent, text="Date Column:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_date = ttk.Entry(parent, width=8)
        self.entry_date.insert(0, self.config.get("col_date", "A"))
        self.entry_date.grid(row=0, column=1, sticky=tk.W, padx=(0, 15), pady=2)
        ttk.Label(parent, text="(A = Column 1)", foreground='gray', font=('Arial', 8)).grid(row=0, column=2, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Journal Column:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_journal = ttk.Entry(parent, width=8)
        self.entry_journal.insert(0, self.config.get("col_journal", "C"))
        self.entry_journal.grid(row=0, column=4, sticky=tk.W, padx=(0, 15), pady=2)
        ttk.Label(parent, text="(C = Column 3)", foreground='gray', font=('Arial', 8)).grid(row=0, column=5, sticky=tk.W, pady=2)
        
        # Row 1
        ttk.Label(parent, text="Reference Column:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_reference = ttk.Entry(parent, width=8)
        self.entry_reference.insert(0, self.config.get("col_reference", "G"))
        self.entry_reference.grid(row=1, column=1, sticky=tk.W, padx=(0, 15), pady=2)
        ttk.Label(parent, text="(G = Column 7)", foreground='gray', font=('Arial', 8)).grid(row=1, column=2, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Description Column:").grid(row=1, column=3, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_description = ttk.Entry(parent, width=8)
        self.entry_description.insert(0, self.config.get("col_description", "I"))
        self.entry_description.grid(row=1, column=4, sticky=tk.W, padx=(0, 15), pady=2)
        ttk.Label(parent, text="(I = Column 9)", foreground='gray', font=('Arial', 8)).grid(row=1, column=5, sticky=tk.W, pady=2)
        
        # Row 2
        ttk.Label(parent, text="Debit Column:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_debit = ttk.Entry(parent, width=8)
        self.entry_debit.insert(0, self.config.get("col_debit", "W"))
        self.entry_debit.grid(row=2, column=1, sticky=tk.W, padx=(0, 15), pady=2)
        ttk.Label(parent, text="(W = Column 23)", foreground='gray', font=('Arial', 8)).grid(row=2, column=2, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Credit Column:").grid(row=2, column=3, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_credit = ttk.Entry(parent, width=8)
        self.entry_credit.insert(0, self.config.get("col_credit", "auto"))
        self.entry_credit.grid(row=2, column=4, sticky=tk.W, padx=(0, 15), pady=2)
        ttk.Label(parent, text="('auto' or column letter)", foreground='gray', font=('Arial', 8)).grid(row=2, column=5, sticky=tk.W, pady=2)
        
        # Row 3 - Balance and Account columns
        ttk.Label(parent, text="Balance Columns:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_balance_start = ttk.Entry(parent, width=6)
        self.entry_balance_start.insert(0, self.config.get("col_balance_start", "AF"))
        self.entry_balance_start.grid(row=3, column=1, sticky=tk.W, padx=(0, 5), pady=2)
        
        ttk.Label(parent, text="to").grid(row=3, column=1, sticky=tk.W, padx=(45, 0), pady=2)
        
        self.entry_balance_end = ttk.Entry(parent, width=6)
        self.entry_balance_end.insert(0, self.config.get("col_balance_end", "AF"))
        self.entry_balance_end.grid(row=3, column=1, sticky=tk.W, padx=(65, 0), pady=2)
        
        ttk.Label(parent, text="(AF = Column 32)", foreground='gray', font=('Arial', 8)).grid(row=3, column=2, sticky=tk.W, pady=2)
        
        ttk.Label(parent, text="Account Code Column:").grid(row=3, column=3, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_account_code = ttk.Entry(parent, width=8)
        self.entry_account_code.insert(0, self.config.get("col_account_code", "E"))
        self.entry_account_code.grid(row=3, column=4, sticky=tk.W, padx=(0, 15), pady=2)
        ttk.Label(parent, text="(E = Column 5)", foreground='gray', font=('Arial', 8)).grid(row=3, column=5, sticky=tk.W, pady=2)
        
        # Row 4 - Account Name
        ttk.Label(parent, text="Account Name Column:").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_account_name = ttk.Entry(parent, width=8)
        self.entry_account_name.insert(0, self.config.get("col_account_name", "K"))
        self.entry_account_name.grid(row=4, column=1, sticky=tk.W, padx=(0, 15), pady=2)
        ttk.Label(parent, text="(K = Column 11)", foreground='gray', font=('Arial', 8)).grid(row=4, column=2, sticky=tk.W, pady=2)

    def browse_file(self):
        """Browse for Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.log_message(f"✅ File loaded: {os.path.basename(file_path)}")
            
            # Try to auto-detect columns
            self.auto_detect()

    def column_letter_to_number(self, column_letter):
        """Convert Excel column letter to 0-based number"""
        if not column_letter or column_letter.lower() == 'auto':
            return 'auto'
        
        letters = column_letter.upper().replace('[^A-Z]', '')
        number = 0
        
        for i, char in enumerate(letters[::-1]):
            number += (ord(char) - 64) * (26 ** i)
        
        return number - 1

    def column_number_to_letter(self, column_number):
        """Convert 0-based number to Excel column letter"""
        if column_number < 0:
            return ''
        
        letters = ''
        num = column_number + 1
        
        while num > 0:
            num, remainder = divmod(num - 1, 26)
            letters = chr(65 + remainder) + letters
        
        return letters

    def is_account_line(self, text):
        """Check if text contains account information"""
        if not text:
            return False
        text_lower = str(text).lower()
        return ('account code' in text_lower or 
                'account' in text_lower and 'code' in text_lower)

    def extract_account_info(self, row):
        """Extract account code and name from row"""
        row_text = ' '.join(str(cell) for cell in row if cell)
        
        # Method 1: Look for "ACCOUNT CODE:" pattern
        if self.is_account_line(row_text):
            # Pattern like "ACCOUNT CODE: 12399-D01 ATTACHMENT ALLOWANCES..."
            match = re.search(r'account\s*code[:\s]*([^\s]+)\s*(.*)', row_text, re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                name = match.group(2).strip()
                if code and any(c.isalnum() for c in code):
                    return code, name
        
        # Method 2: Check specific columns for account codes
        account_code_col = self.column_letter_to_number(self.config.get("col_account_code", "E"))
        account_name_col = self.column_letter_to_number(self.config.get("col_account_name", "K"))
        
        if account_code_col != 'auto' and account_code_col < len(row):
            code_candidate = str(row[account_code_col]).strip()
            # Check if it looks like an account code (numbers, dashes, etc.)
            if code_candidate and re.match(r'^[\d\-A-Z]+$', code_candidate) and len(code_candidate) > 2:
                name_candidate = ""
                if account_name_col != 'auto' and account_name_col < len(row):
                    name_candidate = str(row[account_name_col]).strip()
                return code_candidate, name_candidate
        
        # Method 3: Look for patterns like "12399-D01" anywhere in row
        for cell in row:
            cell_str = str(cell).strip()
            # Pattern for account codes like 12399-D01, 14101-A01, etc.
            if re.match(r'^\d{4,5}-[A-Z]\d{2}$', cell_str):
                return cell_str, "Detected Account"
        
        return None, None

    def auto_detect(self):
        """Auto-detect columns from the loaded file"""
        if not self.file_path:
            messagebox.showwarning("Warning", "Please load a file first")
            return
        
        try:
            self.df = pd.read_excel(self.file_path, header=None, engine='openpyxl')
            rows = self.df.head(20).fillna('').astype(str).values.tolist()
            
            detected = {}
            
            for i, row in enumerate(rows):
                for col_idx, cell in enumerate(row):
                    cell_lower = cell.lower().strip()
                    
                    if 'date' in cell_lower and 'date' not in detected:
                        detected['date'] = col_idx
                    elif ('journal' in cell_lower or 'journ' in cell_lower) and 'journal' not in detected:
                        detected['journal'] = col_idx
                    elif ('ref' in cell_lower or 'reference' in cell_lower) and 'reference' not in detected:
                        detected['reference'] = col_idx
                    elif ('desc' in cell_lower or 'description' in cell_lower) and 'description' not in detected:
                        detected['description'] = col_idx
                    elif 'debit' in cell_lower and 'debit' not in detected:
                        detected['debit'] = col_idx
                    elif 'credit' in cell_lower and 'credit' not in detected:
                        detected['credit'] = col_idx
                    elif 'balance' in cell_lower and 'balance' not in detected:
                        detected['balance'] = col_idx
                    elif ('account' in cell_lower and 'code' in cell_lower) and 'account_code' not in detected:
                        detected['account_code'] = col_idx
            
            # Update UI with detected columns
            if 'date' in detected:
                self.entry_date.delete(0, tk.END)
                self.entry_date.insert(0, self.column_number_to_letter(detected['date']))
            
            if 'journal' in detected:
                self.entry_journal.delete(0, tk.END)
                self.entry_journal.insert(0, self.column_number_to_letter(detected['journal']))
            
            if 'reference' in detected:
                self.entry_reference.delete(0, tk.END)
                self.entry_reference.insert(0, self.column_number_to_letter(detected['reference']))
            
            if 'description' in detected:
                self.entry_description.delete(0, tk.END)
                self.entry_description.insert(0, self.column_number_to_letter(detected['description']))
            
            if 'debit' in detected:
                self.entry_debit.delete(0, tk.END)
                self.entry_debit.insert(0, self.column_number_to_letter(detected['debit']))
            
            if 'balance' in detected:
                self.entry_balance_start.delete(0, tk.END)
                self.entry_balance_start.insert(0, self.column_number_to_letter(detected['balance']))
                self.entry_balance_end.delete(0, tk.END)
                self.entry_balance_end.insert(0, self.column_number_to_letter(detected['balance']))
            
            if 'account_code' in detected:
                self.entry_account_code.delete(0, tk.END)
                self.entry_account_code.insert(0, self.column_number_to_letter(detected['account_code']))
            
            self.log_message("✅ Auto-detection completed!")
            
            # Show detected columns
            detected_text = "Detected: " + ", ".join(
                [f"{key.title().replace('_', ' ')}={self.column_number_to_letter(val)}" 
                 for key, val in detected.items()])
            self.log_message(detected_text)
            
        except Exception as e:
            self.log_message(f"❌ Auto-detection failed: {str(e)}")

    def get_current_config(self):
        """Get current configuration from UI"""
        return {
            "col_date": self.entry_date.get().strip().upper() or "A",
            "col_journal": self.entry_journal.get().strip().upper() or "C",
            "col_reference": self.entry_reference.get().strip().upper() or "G", 
            "col_description": self.entry_description.get().strip().upper() or "I",
            "col_debit": self.entry_debit.get().strip().upper() or "W",
            "col_credit": self.entry_credit.get().strip(),
            "col_balance_start": self.entry_balance_start.get().strip().upper() or "AF",
            "col_balance_end": self.entry_balance_end.get().strip().upper() or "AF",
            "col_account_code": self.entry_account_code.get().strip().upper() or "E",
            "col_account_name": self.entry_account_name.get().strip().upper() or "K"
        }

    def reset_config(self):
        """Reset configuration to defaults"""
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, "A")
        
        self.entry_journal.delete(0, tk.END)
        self.entry_journal.insert(0, "C")
        
        self.entry_reference.delete(0, tk.END)
        self.entry_reference.insert(0, "G")
        
        self.entry_description.delete(0, tk.END)
        self.entry_description.insert(0, "I")
        
        self.entry_debit.delete(0, tk.END)
        self.entry_debit.insert(0, "W")
        
        self.entry_credit.delete(0, tk.END)
        self.entry_credit.insert(0, "auto")
        
        self.entry_balance_start.delete(0, tk.END)
        self.entry_balance_start.insert(0, "AF")
        
        self.entry_balance_end.delete(0, tk.END)
        self.entry_balance_end.insert(0, "AF")
        
        self.entry_account_code.delete(0, tk.END)
        self.entry_account_code.insert(0, "E")
        
        self.entry_account_name.delete(0, tk.END)
        self.entry_account_name.insert(0, "K")
        
        self.log_message("✅ Configuration reset to defaults!")

    def process_file(self):
        """Process the selected file"""
        if not self.file_path:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        
        # Update config from UI
        self.config.update(self.get_current_config())
        
        # Run processing in thread to avoid GUI freeze
        thread = threading.Thread(target=self._process_file_thread)
        thread.daemon = True
        thread.start()

    def _process_file_thread(self):
        """Process file in separate thread"""
        try:
            self.root.after(0, self._update_ui_processing_start)
            
            # Read file
            self.df = pd.read_excel(self.file_path, header=None, engine='openpyxl')
            rows = self.df.fillna('').values.tolist()
            
            # Convert config to column numbers
            number_config = {}
            for key, value in self.config.items():
                if key.startswith('col_'):
                    number_config[key] = self.column_letter_to_number(value)
            
            # Process data with account detection
            processed_data = []
            current_account_code = "Unknown"
            current_account_name = "Unknown Account"
            
            for i, row in enumerate(rows):
                # Update progress
                if i % 100 == 0:
                    progress = (i / len(rows)) * 100
                    self.root.after(0, lambda p=progress: self.progress.config(value=p))
                
                # Check for account information
                account_code, account_name = self.extract_account_info(row)
                if account_code:
                    current_account_code = account_code
                    if account_name:
                        current_account_name = account_name
                    self.log_message(f"🔍 Found account: {account_code} - {account_name}")
                    continue
                
                # Extract transaction data
                date_val = self._get_cell_value(row, number_config.get('col_date', 0))
                journal_val = self._get_cell_value(row, number_config.get('col_journal', 2))
                ref_val = self._get_cell_value(row, number_config.get('col_reference', 6))
                desc_val = self._get_cell_value(row, number_config.get('col_description', 8))
                debit_val = self._get_cell_value(row, number_config.get('col_debit', 22))
                credit_val = self._get_cell_value(row, number_config.get('col_credit', 'auto'))
                balance_val = self._get_cell_value(row, number_config.get('col_balance_start', 31))
                
                # Auto-detect credit if set to auto
                if credit_val == 'auto' or not credit_val:
                    credit_val = self._auto_detect_credit(row, number_config)
                
                # Check if this is a transaction row
                if self._is_transaction_row(date_val, ref_val, debit_val, credit_val):
                    processed_data.append({
                        'Account Code': current_account_code,
                        'Account Name': current_account_name,
                        'Date': date_val,
                        'Journal': journal_val,
                        'Reference': ref_val,
                        'Description': desc_val,
                        'Debit': debit_val,
                        'Credit': credit_val,
                        'Balance': balance_val
                    })
            
            self.processed_data = processed_data
            
            # Update UI on main thread
            self.root.after(0, lambda: self._update_ui_processing_done(processed_data))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Processing error: {str(e)}"))

    def _auto_detect_credit(self, row, number_config):
        """Auto-detect credit amount from row"""
        # Skip debit and balance columns
        skip_cols = []
        if number_config.get('col_debit') != 'auto':
            skip_cols.append(number_config['col_debit'])
        if number_config.get('col_balance_start') != 'auto':
            skip_cols.extend(range(number_config['col_balance_start'], 
                                 number_config.get('col_balance_end', number_config['col_balance_start']) + 1))
        
        # Look for numeric values in other columns
        for col_idx, cell in enumerate(row):
            if col_idx in skip_cols:
                continue
            if self._is_numeric(cell) and float(cell) > 0:
                return cell
        return ""

    def _is_transaction_row(self, date, reference, debit, credit):
        """Check if row contains transaction data"""
        has_date = bool(str(date).strip())
        has_ref = bool(str(reference).strip())
        has_debit = self._is_numeric(debit) and float(debit) > 0
        has_credit = self._is_numeric(credit) and float(credit) > 0
        
        return (has_date and has_ref) or (has_date and (has_debit or has_credit))

    def _get_cell_value(self, row, col_index):
        """Safely get cell value from row"""
        if col_index == 'auto' or col_index >= len(row):
            return ''
        value = row[col_index]
        return value if value is not None else ''

    def _is_numeric(self, value):
        """Check if value is numeric"""
        try:
            float(str(value))
            return True
        except:
            return False

    def _update_ui_processing_start(self):
        """Update UI when processing starts"""
        self.progress.config(value=0)
        self.log_message("🔄 Processing file...")
        self.export_csv_btn.config(state=tk.DISABLED)
        self.export_excel_btn.config(state=tk.DISABLED)
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _update_ui_processing_done(self, processed_data):
        """Update UI when processing is done"""
        self.progress.config(value=100)
        self.log_message(f"✅ PROCESSING COMPLETE! Found {len(processed_data)} transactions")
        self.log_message(f"📊 Accounts detected: {len(set([d['Account Code'] for d in processed_data]))} unique account codes")
        
        # Enable export buttons
        self.export_csv_btn.config(state=tk.NORMAL)
        self.export_excel_btn.config(state=tk.NORMAL)
        
        # Update results table
        self.update_results_table(processed_data)
        
        # Show export instructions
        self.log_message("💡 **NEXT STEP:** Click 'EXPORT AS CSV' or 'EXPORT AS EXCEL' above to save your file!")
        self.log_message("   The file will be saved wherever you choose on your computer")

    def update_results_table(self, data):
        """Update the results table with processed data"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new data
        for row in data[:500]:  # Limit to 500 rows for performance
            self.tree.insert('', tk.END, values=(
                row.get('Account Code', ''),
                row.get('Account Name', ''),
                row.get('Date', ''),
                row.get('Journal', ''),
                row.get('Reference', ''),
                row.get('Description', ''),
                row.get('Debit', ''),
                row.get('Credit', ''),
                row.get('Balance', '')
            ))
        
        self.log_message(f"📊 Displaying {min(len(data), 500)} of {len(data)} rows in preview")

    def export_csv(self):
        """Export processed data to CSV"""
        if not self.processed_data:
            messagebox.showwarning("Warning", "No data to export. Please process a file first.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save As CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="cleaned_ledger_with_accounts.csv"
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.processed_data)
                df.to_csv(file_path, index=False)
                self.log_message(f"✅ CSV file saved: {file_path}")
                messagebox.showinfo("Success", f"File saved successfully!\n\n{file_path}")
            except Exception as e:
                self.log_message(f"❌ Export failed: {str(e)}")
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def export_excel(self):
        """Export processed data to Excel"""
        if not self.processed_data:
            messagebox.showwarning("Warning", "No data to export. Please process a file first.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save As Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="cleaned_ledger_with_accounts.xlsx"
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.processed_data)
                df.to_excel(file_path, index=False, engine='openpyxl')
                self.log_message(f"✅ Excel file saved: {file_path}")
                messagebox.showinfo("Success", f"File saved successfully!\n\n{file_path}")
            except Exception as e:
                self.log_message(f"❌ Export failed: {str(e)}")
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def log_message(self, message):
        """Add message to diagnostic area"""
        self.diagnostic_text.insert(tk.END, message + "\n")
        self.diagnostic_text.see(tk.END)
        self.diagnostic_text.update()

def main():
    root = tk.Tk()
    app = AuditorAppUniversal(root)
    root.mainloop()

if __name__ == "__main__":
    main()