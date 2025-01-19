import tkinter as tk


class StatusBar:
    """
    A status bar widget to display application status messages.
    """

    def __init__(self, root):
        self.status_var = tk.StringVar(value="Status: Ready")
        self.status_label = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, text: str):
        """
        Updates the status message displayed on the status bar.

        Args:
            :param text: The status message to display.
        """
        self.status_var.set(text)
