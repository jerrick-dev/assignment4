import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ds_messenger import DirectMessenger, DirectMessage
from Profile import Profile

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x150")

        # Login Frame
        self.login_frame = tk.Frame(self.root, padx=20, pady=20)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        # Username
        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, sticky=tk.W)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, sticky=tk.EW)

        # Password
        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, sticky=tk.W)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky=tk.EW)

        # IP/Server Address
        self.server_label = tk.Label(self.login_frame, text="Server Address:")
        self.server_label.grid(row=2, column=0, sticky=tk.W)
        self.server_entry = tk.Entry(self.login_frame)
        self.server_entry.grid(row=2, column=1, sticky=tk.EW)

        # Login Button
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        address = self.server_entry.get().strip()

        if not username or not password or not address:
            messagebox.showwarning("Error", "Please enter username, password, and server.")
            return

        # Initialize DirectMessenger
        dsuserver = address
        try:
            messenger = DirectMessenger(dsuserver, username, password)
            self.root.destroy()  # Close the login window
            open_chat_app(username, password, dsuserver, messenger)
        except Exception as e:
            messagebox.showerror("Login Failed", f"Failed to login: {e}")


class MessengerGUI:
    def __init__(self, root, username, password, dsuserver, messenger):
        self.root = root
        self.root.title(f"DS Messenger - {username}")
        self.root.geometry("800x600")

        self.username = username
        self.password = password
        self.dsuserver = dsuserver
        self.messenger = messenger

        # GUI Layout
        self.create_widgets()

        # Schedule periodic message updates
        self.update_messages()

    def create_widgets(self):
        # Top Panel: Recipient Selection
        self.top_panel = tk.Frame(self.root, bg="#f8f9fa")
        self.top_panel.pack(fill=tk.X, padx=10, pady=10)

        self.recipient_label = tk.Label(self.top_panel, text="Recipient:", bg="#f8f9fa")
        self.recipient_label.pack(side=tk.LEFT, padx=(0, 10))

        self.recipient_var = tk.StringVar()
        self.recipient_dropdown = ttk.Combobox(self.top_panel, textvariable=self.recipient_var, state="readonly")
        self.recipient_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.recipient_dropdown.bind("<<ComboboxSelected>>", self.on_recipient_select)

        # Chat Display
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED, bg="white", fg="black")
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Message Entry Panel
        self.entry_panel = tk.Frame(self.root, bg="#f8f9fa")
        self.entry_panel.pack(fill=tk.X, padx=10, pady=10)

        self.message_entry = tk.Entry(self.entry_panel, bg="white", fg="black")
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.entry_panel, text="Send", bg="#0095f6", fg="white", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        # Load Recipients
        self.load_recipients()

    def load_recipients(self):
        """Load recipients from the server."""
        # This is a placeholder. You should replace this with actual logic to fetch existing users from the server.
        existing_users = ["user1", "user2", "user3"]  # Replace with actual user list from server
        self.recipient_dropdown["values"] = existing_users
        if existing_users:
            self.recipient_dropdown.current(0)
            self.selected_recipient = existing_users[0]
            self.load_messages(self.selected_recipient)

    def on_recipient_select(self, event=None):
        """Handle recipient selection and load their messages."""
        self.selected_recipient = self.recipient_var.get()
        self.load_messages(self.selected_recipient)

    def load_messages(self, recipient):
        """Load messages for the selected recipient."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)

        # Retrieve all messages for the recipient
        messages = self.messenger.retrieve_all()
        for msg in messages:
            if msg.recipient == recipient or msg.sender == recipient:
                self.display_message(msg)

        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.yview(tk.END)  # Scroll to the bottom

    def display_message(self, message):
        """Display a message in the chat window."""
        sender = message.sender if message.sender != self.username else "You"
        timestamp = message.timestamp
        msg_text = f"{sender} ({timestamp}): {message.message}\n"
        self.chat_display.insert(tk.END, msg_text)

    def send_message(self, event=None):
        """Send a message to the selected recipient."""
        message_text = self.message_entry.get().strip()
        if not message_text:
            messagebox.showwarning("Empty Message", "Please enter a message.")
            return

        if not hasattr(self, 'selected_recipient'):
            messagebox.showwarning("No Recipient", "Please select a recipient.")
            return

        # Check if the recipient exists on the server
        existing_users = self.recipient_dropdown["values"]
        if self.selected_recipient not in existing_users:
            messagebox.showerror("Error", f"Recipient '{self.selected_recipient}' does not exist.")
            return

        # Send the message
        success = self.messenger.send(message_text, self.selected_recipient)
        if success:
            self.message_entry.delete(0, tk.END)
            self.load_messages(self.selected_recipient)
        else:
            messagebox.showerror("Error", "Failed to send message.")

    def update_messages(self):
        """Periodically check for new messages and update the chat display."""
        if hasattr(self, 'selected_recipient'):
            # Retrieve new messages
            new_messages = self.messenger.retrieve_new()
            for msg in new_messages:
                if msg.sender == self.selected_recipient or msg.recipient == self.selected_recipient:
                    self.display_message(msg)

        # Schedule the function to run again after 5 seconds
        self.root.after(5000, self.update_messages)

    def run(self):
        """Run the GUI."""
        self.root.mainloop()

    def run(self):
        """Run the GUI."""
        self.root.mainloop()


def open_chat_app(username, password, dsuserver, messenger):
    """Open the chat application after successful login."""
    root = tk.Tk()
    app = MessengerGUI(root, username, password, dsuserver, messenger)
    app.run()


if __name__ == "__main__":
    root = tk.Tk()
    login_screen = LoginScreen(root)
    root.mainloop()  