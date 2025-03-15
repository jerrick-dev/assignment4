import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
from datetime import datetime
from ds_messenger import DirectMessenger
from Profile import *

class Body(tk.Frame):
      def __init__(self, root, recipient_selected_callback=None):
            tk.Frame.__init__(self, root, bg="#36393F")
            self.root = root
            self._contacts = []
            self._select_callback = recipient_selected_callback
            self._draw()

      def node_select(self, event):
            selected_item = self.contacts_tree.selection()
            if selected_item:
                  contact = self.contacts_tree.item(selected_item, "values")[0]  # Get the contact name from the first column
                  if self._select_callback:
                        self._select_callback(contact)

      def insert_contact(self, contact: str):
            if contact not in self._contacts:
                  self._contacts.append(contact)
                  self._insert_contact_tree(contact)

      def _insert_contact_tree(self, contact: str):
            self.contacts_tree.insert("", "end", values=(contact,)) 

      def insert_user_message(self, message: str):
            self.chat_area.configure(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"You\n", "username")
            timestamp = datetime.now().strftime("%H:%M")
            self.chat_area.insert(tk.END, f"{timestamp}\n", "timestamp")
            self.chat_area.insert(tk.END, f" {message} \n", "user")
            self.chat_area.configure(state=tk.DISABLED)
            self.chat_area.yview(tk.END)

      def insert_contact_message(self, recipient, message: str):
            self.chat_area.configure(state=tk.NORMAL)
            self.chat_area.insert(tk.END, f"{recipient}\n", "username")
            timestamp = datetime.now().strftime("%H:%M")
            self.chat_area.insert(tk.END, f"{timestamp}\n", "timestamp")
            self.chat_area.insert(tk.END, f" {message} \n", "contact")
            self.chat_area.configure(state=tk.DISABLED)
            self.chat_area.yview(tk.END)

      def get_text_entry(self) -> str:
            return self.message_entry.get("1.0", tk.END).strip()

      def set_text_entry(self, text: str):
            self.message_entry.delete("1.0", tk.END)
            self.message_entry.insert("1.0", text)

      def _draw(self):
            # Sidebar for contacts
            sidebar = tk.Frame(self, bg="#2F3136", width=200)
            sidebar.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)

            # Initialize Treeview with a column
            self.contacts_tree = ttk.Treeview(sidebar, columns=("contact"), show="headings", selectmode="browse")
            self.contacts_tree.heading("contact", text="Contacts") 
            self.contacts_tree.column("contact", stretch=tk.YES) 
            self.contacts_tree.bind("<<TreeviewSelect>>", self.node_select)
            self.contacts_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Main chat area
            chat_frame = tk.Frame(self, bg="#36393F")
            chat_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)

            self.chat_area = scrolledtext.ScrolledText(
                  chat_frame, wrap=tk.WORD, state=tk.DISABLED, bg="#36393F", fg="white", font=("Helvetica", 8)
            )
            self.chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Message input box
            self.message_entry = tk.Text(chat_frame, height=3, bg="#40444B", fg="white", font=("Arial", 12))
            self.message_entry.pack(fill=tk.X, padx=5, pady=5)

            self.chat_area.tag_configure("timestamp", foreground="#72767D", font=("Arial", 10))
            self.chat_area.tag_configure("user", foreground="#FFFFFF", background="#7289DA", 
                                          lmargin1=20, lmargin2=20, rmargin=20, 
                                          spacing1=5, spacing3=5, relief="raised", borderwidth=2)
            self.chat_area.tag_configure("contact", foreground="#000000", background="#FFFFFF", 
                                          lmargin1=20, lmargin2=20, rmargin=20, 
                                          spacing1=5, spacing3=5, relief="raised", borderwidth=2)


class Footer(tk.Frame):
      def __init__(self, root, send_callback=None):
            tk.Frame.__init__(self, root, bg="#2F3136")
            self.root = root
            self._send_callback = send_callback
            self._draw()

      def send_click(self):
            if self._send_callback:
                  self._send_callback()

      def _draw(self):
        send_button = tk.Button(
            self, text="Send", bg="#7289DA", fg="white", font=("Arial", 12), command=self.send_click
        )
        send_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.footer_label = tk.Label(self, text="Ready.", bg="#2F3136", fg="white", font=("Arial", 10))
        self.footer_label.pack(side=tk.LEFT, padx=10, pady=10)


class NewContactDialog(simpledialog.Dialog):
    def __init__(self, root, title=None, user=None, pwd=None, server=None):
        self.root = root
        self.server = server
        self.user = user
        self.pwd = pwd
        super().__init__(root, title)

    def body(self, frame):
        self.server_label = tk.Label(frame, text="DS Server Address", bg="#36393F", fg="white")
        self.server_label.pack()
        self.server_entry = tk.Entry(frame, bg="#40444B", fg="white")
        self.server_entry.insert(tk.END, self.server)
        self.server_entry.pack()

        self.username_label = tk.Label(frame, text="Username", bg="#36393F", fg="white")
        self.username_label.pack()
        self.username_entry = tk.Entry(frame, bg="#40444B", fg="white")
        self.username_entry.insert(tk.END, self.user)
        self.username_entry.pack()

        self.password_label = tk.Label(frame, text="Password", bg="#36393F", fg="white")
        self.password_label.pack()
        self.password_entry = tk.Entry(frame, bg="#40444B", fg="white", show="*")
        self.password_entry.pack()

    def apply(self):
        self.user = self.username_entry.get()
        self.pwd = self.password_entry.get()
        self.server = self.server_entry.get()


class MainApp(tk.Frame):
        def __init__(self, root, messenger):
            tk.Frame.__init__(self, root, bg="#36393F")
            self.root = root
            self.messenger = messenger
            self.username = messenger.username
            self.password = messenger.password
            self.server = messenger.dsuserver
            self.recipient = None
            self.profile = Profile(self.server,self.username,self.password)
            self.check = Profile(self.server,self.username,self.password)
            try:
                  #checks account details to load proper contacts and etc;
                  self.profile.load_profile("profile.dsu",self.username)
                  if self.check.username != self.profile.username:
                        self.profile=self.check
                        self.profile.save_profile("profile.dsu",self.username)
                  else:
                        self.profile.load_profile("profile.dsu",self.username)
                  

            except DsuFileError:
                 self.profile.save_profile("profile.dsu",self.username)
            
            self._draw()

        def send_message(self):
            message = self.body.get_text_entry()
            if message and self.recipient:
                  if self.messenger.send(message, self.recipient):
                        if self.recipient not in self.body._contacts:
                              self.body.insert_contact(self.recipient)
      
                        #local save
                        self.profile.add_rec(self.recipient)
                        self.profile.add_msg({
                              "sender": self.username,
                              "recipient": self.recipient,
                              "message": message,
                              "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                        self.body.insert_user_message(message)
                        self.body.set_text_entry("")
                        self.profile.save_profile("profile.dsu",self.username)
                  else:
                        messagebox.showerror("Error", "User does not exist!")
                  
        def add_contact(self):
            contact = simpledialog.askstring("Add Contact", "Enter the username of the new contact:")
            if contact:
                self.body.insert_contact(contact)
            
        def display_message(self, message):
            sender = message.get("sender", "Unknown")
            if sender == self.username:
                  sender = "You"
            timestamp = message.get("timestamp", "Unknown")
            msg_text = f"{sender} ({timestamp}): {message.get('message', '')}\n"
            self.body.chat_area.insert(tk.END, msg_text)

        def load_messages(self, recipient):
            self.body.chat_area.configure(state=tk.NORMAL)
            self.body.chat_area.delete(1.0, tk.END)

            # Retrieve all messages for the recipient
            if self.profile.messages:
                  for msg in self.profile.messages:
                        if (msg["sender"] == self.username and msg["recipient"] == recipient) or \
                        (msg["sender"] == recipient and msg["recipient"] == self.username):
                              self.display_message(msg)
            self.body.chat_area.configure(state=tk.DISABLED)
            self.body.chat_area.yview(tk.END) 

        def recipient_selected(self, recipient):
            self.recipient = recipient
            self.body.chat_area.configure(state=tk.NORMAL)
            self.body.chat_area.delete(1.0, tk.END)
            
            for msg in self.profile.messages:
                  if (msg["sender"] == self.username and msg["recipient"]  == recipient) or (msg["sender"] == recipient and msg["recipient"] == self.username):
                        if msg["sender"] == self.username:
                              self.body.insert_user_message(msg["message"])
                        else:
                              self.body.insert_contact_message(recipient,msg["message"])

            self.body.chat_area.configure(state=tk.DISABLED)
            self.body.chat_area.yview(tk.END)


        def configure_server(self):
            dialog = NewContactDialog(self.root, "Configure Account", self.username, self.password, self.server)
            self.username = dialog.user
            self.password = dialog.pwd
            self.server = dialog.server

        def check_new(self):
            new_messages = self.messenger.retrieve_new()
            if new_messages is None:
                  new_messages=[]

            for msg in new_messages:
                  if msg.sender == self.recipient or msg.recipient == self.recipient:
                        if msg.sender not in self.body._contacts:
                              self.body.insert_contact(msg.sender)

                        if msg.sender == self.recipient:
                              self.profile.add_msg({
                                    "sender": self.recipient,
                                    "recipient": self.username,
                                    "message": msg.message,
                                    "timestamp": msg.timestamp
                                    })
                              self.body._insert_contact_tree(self.recipient) 
                              self.body.insert_contact_message(self.recipient,msg.message)
                        else:
                              self.profile.add_msg({
                              "sender": self.username,
                              "recipient": self.recipient,
                              "message": msg.message,
                              "timestamp": msg.timestamp
                              })
                              self.body.insert_user_message(msg.message)
                              
            self.profile.save_profile("profile.dsu",self.username)
            self.root.after(500, self.check_new)

        def _draw(self):
            menu_bar = tk.Menu(self.root, bg="#2F3136", fg="white")
            self.root['menu'] = menu_bar

            file_menu = tk.Menu(menu_bar, tearoff=0, bg="#2F3136", fg="white")
            menu_bar.add_cascade(menu=file_menu, label=self.username)
            file_menu.add_command(label='New')
            file_menu.add_command(label='Open...')
            file_menu.add_command(label='Close')

            settings_menu = tk.Menu(menu_bar, tearoff=0, bg="#2F3136", fg="white")
            menu_bar.add_cascade(menu=settings_menu, label='Settings')
            settings_menu.add_command(label='Add Contact', command=self.add_contact)
            settings_menu.add_command(label='Configure DS Server', command=self.configure_server)

            # Body and Footer
            self.body = Body(self.root, recipient_selected_callback=self.recipient_selected)
            self.body.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
            self.footer = Footer(self.root, send_callback=self.send_message)
            self.footer.pack(fill=tk.X, side=tk.BOTTOM)

            self.load_con()
            # Start checking for new messages
            self.check_new()
            
        def load_con(self):
                #insertknowncontacts
            for id in self.profile.recipients:
                  self.body._insert_contact_tree(id) 



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
            #   self.server_label = tk.Label(self.login_frame, text="Server Address:")
            #   self.server_label.grid(row=2, column=0, sticky=tk.W)
            #   self.server_entry = tk.Entry(self.login_frame)
            #   self.server_entry.grid(row=2, column=1, sticky=tk.EW)

            # Login Button
            self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
            self.login_button.grid(row=3, column=0, columnspan=2, pady=10)

      def login(self):
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            #address = self.server_entry.get().strip()

            if not username or not password:
                  messagebox.showwarning("Error", "Please enter username, password, and server.")
                  return

            # Initialize DirectMessenger
            dsuserver = "127.0.0.1"
            try:
                  messenger = DirectMessenger(dsuserver, username, password)
                  self.root.destroy()
                  root = tk.Tk()
                  app = MainApp(root, messenger)
                  root.mainloop()
            except Exception as e:
                  messagebox.showerror("Login Failed", f"Failed to login: {e}")


def gui_start():
    root = tk.Tk()
    root.title("ICS 32 Distributed Social Messenger")
    root.geometry("800x600")
    root.configure(bg="#36393F")
    login_screen = LoginScreen(root)
    root.mainloop()