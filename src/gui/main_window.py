import customtkinter

from src.gui import file_tab, map_tab

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Main window configurations
        self.title("Compass")
        self.minsize(1000, 725)

        # Configure grid for the Compass tab view
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Configure tab view for Compass app
        self.compass_tab_view = CompassTabView(master=self)
        self.compass_tab_view.grid(row=0, column=0, padx=20, pady=20, sticky='nswe')
        self.compass_tab_view._segmented_button.configure(font=('Segoe UI', -13, 'bold'))


class CompassTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Create two tabs to handle input from a file and from map
        self.add('Input from File')
        self.add('Input from Map')

        self._tab_dict['Input from File'] = file_tab.FileTab(master=self)
        self._tab_dict['Input from Map'] = map_tab.MapTab(master=self)

        self.set('Input from File')
