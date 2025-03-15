from Profile import Profile  # Import the Profile class
from ds_messenger import DirectMessenger  # Import the DirectMessenger class
from a4 import DirectMessengerGUI  # Import the DirectMessengerGUI class
import tkinter as tk

if __name__ == "__main__":
    # Create a Profile instance

    # Create a DirectMessenger instance
    messenger = DirectMessenger(dsuserver='127.0.0.1', username="user1", password="password123")

    # Create the Tkinter root window
    root = tk.Tk()

    # Create the GUI
    gui = DirectMessengerGUI(root, messenger)

    # Start the Tkinter event loop
    root.mainloop()