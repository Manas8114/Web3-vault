import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import hashlib
import json
import os
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import threading
import time

class DecentralizedVault:
    def __init__(self, location):
        self.location = location
        self.data = {}
        self.access_control = {}
        self.search_index = {}
        self.key_file = f"{self.location}_key.key"
        self.load_or_create_key()
        self.cipher_suite = Fernet(self.key)
        self.load_data()

    def load_or_create_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as key_file:
                self.key = key_file.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(self.key)

    def encrypt_data(self, data):
        return self.cipher_suite.encrypt(json.dumps(data).encode())

    def decrypt_data(self, encrypted_data):
        try:
            return json.loads(self.cipher_suite.decrypt(encrypted_data).decode())
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return None

    def store_data(self, data, metadata=None, shared_with=None, expiration=None):
        data_id = hashlib.sha256(json.dumps(data).encode()).hexdigest()
        encrypted_data = self.encrypt_data(data)
        self.data[data_id] = {
            'encrypted_data': encrypted_data,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        self._update_search_index(data_id, data)
        if shared_with:
            self.share_data(data_id, shared_with, expiration)
        self.save_data()
        return data_id

    def _update_search_index(self, data_id, data):
        for key, value in data.items():
            if isinstance(value, str):
                for word in value.lower().split():
                    if word not in self.search_index:
                        self.search_index[word] = set()
                    self.search_index[word].add(data_id)

    def retrieve_data(self, data_id):
        if data_id in self.data:
            encrypted_data = self.data[data_id]['encrypted_data']
            return self.decrypt_data(encrypted_data)
        return None

    def search_data(self, query):
        results = set()
        for word in query.lower().split():
            if word in self.search_index:
                results.update(self.search_index[word])
        return [self.retrieve_data(data_id) for data_id in results if self.retrieve_data(data_id) is not None]

    def share_data(self, data_id, recipients, expiration_days=None):
        if data_id not in self.data:
            raise ValueError("Data not found")
        
        if data_id not in self.access_control:
            self.access_control[data_id] = {}
        
        expiration = None
        if expiration_days:
            expiration = (datetime.now() + timedelta(days=expiration_days)).isoformat()
        
        for recipient in recipients:
            self.access_control[data_id][recipient] = {
                'granted_at': datetime.now().isoformat(),
                'expires_at': expiration
            }
        self.save_data()

    def revoke_access(self, data_id, recipient):
        if data_id in self.access_control and recipient in self.access_control[data_id]:
            del self.access_control[data_id][recipient]
            self.save_data()

    def has_access(self, data_id, recipient):
        if data_id not in self.access_control or recipient not in self.access_control[data_id]:
            return False
        
        access_info = self.access_control[data_id][recipient]
        if access_info['expires_at']:
            expiration = datetime.fromisoformat(access_info['expires_at'])
            if expiration < datetime.now():
                return False
        
        return True

    def cleanup_expired_access(self):
        current_time = datetime.now().isoformat()
        for data_id, access_info in list(self.access_control.items()):
            for recipient, info in list(access_info.items()):
                if info['expires_at'] and info['expires_at'] < current_time:
                    del access_info[recipient]
        self.save_data()  # Save changes after cleanup

    def sync_data(self, other_vault):
        for data_id, data_info in other_vault.data.items():
            if data_id not in self.data or self.data[data_id]['updated_at'] < data_info['updated_at']:
                self.data[data_id] = data_info

        for data_id, access_info in other_vault.access_control.items():
            if data_id not in self.access_control:
                self.access_control[data_id] = {}
            self.access_control[data_id].update(access_info)

        self.save_data()

    def save_data(self):
        encrypted_data = self.encrypt_data({
            'data': self.data,
            'access_control': self.access_control,
            'search_index': {k: list(v) for k, v in self.search_index.items()}
        })
        with open(f"{self.location}_vault.enc", "wb") as f:
            f.write(encrypted_data)

    def load_data(self):
        try:
            with open(f"{self.location}_vault.enc", "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.decrypt_data(encrypted_data)
            if decrypted_data:
                self.data = decrypted_data['data']
                self.access_control = decrypted_data['access_control']
                self.search_index = {k: set(v) for k, v in decrypted_data['search_index'].items()}
            else:
                print(f"Error: Unable to decrypt data for {self.location}. Starting fresh.")
                self.data = {}
                self.access_control = {}
                self.search_index = {}
        except FileNotFoundError:
            print(f"No existing data found for {self.location}. Starting fresh.")
            self.data = {}
            self.access_control = {}
            self.search_index = {}

class VaultGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Decentralized Vault")
        self.master.geometry("800x600")

        self.vaults = {}
        self.current_vault = None
        self.logged_in = False

        self.setup_login_frame()

    def setup_login_frame(self):
        self.login_frame = ttk.Frame(self.master, padding="10")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, sticky=tk.E, pady=5)

        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky=tk.E, pady=5)

        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(self.login_frame, text="Register", command=self.register).grid(row=3, column=0, columnspan=2)

    def setup_main_frame(self):
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Button(self.main_frame, text="Upload File", command=self.upload_file).grid(row=0, column=0, pady=5)
        ttk.Button(self.main_frame, text="Search", command=self.search_data).grid(row=0, column=1, pady=5)
        ttk.Button(self.main_frame, text="Share", command=self.share_data).grid(row=0, column=2, pady=5)
        ttk.Button(self.main_frame, text="Sync", command=self.sync_vaults).grid(row=0, column=3, pady=5)

        self.file_list = tk.Listbox(self.main_frame, width=50)
        self.file_list.grid(row=1, column=0, columnspan=4, pady=5)

        self.update_file_list()

        # Start automatic sync
        self.start_auto_sync()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.verify_credentials(username, password):
            self.logged_in = True
            self.vaults = {
                'local': DecentralizedVault('local'),
                'cloud': DecentralizedVault('cloud')
            }
            self.current_vault = self.vaults['local']
            self.login_frame.destroy()
            self.setup_main_frame()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.create_user(username, password):
            messagebox.showinfo("Registration Successful", "User created successfully")
        else:
            messagebox.showerror("Registration Failed", "Username already exists")

    def verify_credentials(self, username, password):
        try:
            with open(f"{username}.json", "r") as f:
                user_data = json.load(f)
            return user_data["password"] == hashlib.sha256(password.encode()).hexdigest()
        except FileNotFoundError:
            return False

    def create_user(self, username, password):
        if os.path.exists(f"{username}.json"):
            return False
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with open(f"{username}.json", "w") as f:
            json.dump({"username": username, "password": hashed_password}, f)
        return True

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as file:
                file_content = file.read()

            file_name = os.path.basename(file_path)
            file_type = 'binary' if isinstance(file_content, bytes) else 'text'
            
            # Prepare the data
            if file_type == 'binary':
                content = file_content.hex()  # Convert binary to hex
            else:
                content = file_content.decode('utf-8')  # Assuming text files are UTF-8 encoded
            
            data = {
                'file_name': file_name,
                'file_type': file_type,
                'content': content  # Store the processed content here
            }

            # Get additional metadata
            metadata = simpledialog.askstring("Metadata", "Enter any metadata for the file:")
            
            # Get sharing and expiration info
            shared_with = simpledialog.askstring("Share", "Enter comma-separated list of users to share with (or leave blank):")
            expiration = simpledialog.askinteger("Expiration", "Enter number of days until access expires (or 0 for no expiration):")
            
            shared_with = [user.strip() for user in shared_with.split(',')] if shared_with else None
            expiration = expiration if expiration > 0 else None
            
            # Store the data in the current vault
            data_id = self.current_vault.store_data(data, metadata=metadata, shared_with=shared_with, expiration=expiration)
            
            self.update_file_list()
            messagebox.showinfo("Upload Successful", f"File {file_name} uploaded successfully")

    def search_data(self):
        query = simpledialog.askstring("Search", "Enter search query:")
        if query:
            results = self.current_vault.search_data(query)
            self.display_search_results(results)

    def display_search_results(self, results):
        result_window = tk.Toplevel(self.master)
        result_window.title("Search Results")
        result_window.geometry("400x300")
        
        result_list = tk.Listbox(result_window)
        result_list.pack(fill=tk.BOTH, expand=True)

        for result in results:
            if 'file_name' in result:
                result_list.insert(tk.END, result['file_name'])

        result_list.bind("<Double-1>", lambda event: self.show_file_content(results[result_list.curselection()[0]]))

    def show_file_content(self, file_data):
        content_window = tk.Toplevel(self.master)
        content_window.title("File Content")

        file_content = bytes.fromhex(file_data['content']) if file_data['file_type'] == 'binary' else file_data['content']
        content_text = tk.Text(content_window)
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert(tk.END, file_content.decode('utf-8'))
        content_text.config(state=tk.DISABLED)

    def share_data(self):
        selected_file = self.file_list.curselection()
        if not selected_file:
            messagebox.showwarning("Share Error", "Please select a file to share")
            return

        data_id = self.file_list.get(selected_file[0])
        recipients = simpledialog.askstring("Share", "Enter recipients (comma-separated):")
        expiration_days = simpledialog.askinteger("Expiration", "Enter expiration days (leave blank for no expiration):")

        if recipients:
            recipient_list = [r.strip() for r in recipients.split(",")]
            self.current_vault.share_data(data_id, recipient_list, expiration_days)
            messagebox.showinfo("Share", f"Data shared with: {recipients}")

    def sync_vaults(self):
        other_vault = self.vaults['cloud']  # Simulating syncing with cloud
        self.current_vault.sync_data(other_vault)
        messagebox.showinfo("Sync", "Vaults synced successfully")

    def update_file_list(self):
        self.file_list.delete(0, tk.END)
        for data_id in self.current_vault.data.keys():
            self.file_list.insert(tk.END, data_id)

    def start_auto_sync(self):
        def auto_sync():
            while self.logged_in:
                self.sync_vaults()
                time.sleep(30)
        threading.Thread(target=auto_sync, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = VaultGUI(root)
    root.mainloop()
