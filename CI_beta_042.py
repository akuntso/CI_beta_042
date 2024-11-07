import tkinter as tk 
from tkinter import ttk, messagebox
import requests
import webbrowser
import re

class FileManager:
    """Handles file-related operations"""
    def __init__(self, filename="results.txt"):
        self.filename = filename
    
    def append_to_file(self, data: str) -> None:
        """Appends data to the results file

        :data: data with results and buttons
        """
        with open(self.filename, "a") as file:
            file.write(data + "\n")

    def clear_file(self) -> None:
        """Clears the contents of the results file"""
        open(self.filename, 'w').close()

    def extract_digits(self, text: str) -> str:
        """Extract only numbers from the link for the results.txt file

        :test: text of inputed sha commit
        """
        digits = "".join(re.findall("\d+", text))
        return digits

class UserInterfaseActions:
    """Actions for UI, handles API data fetching logic"""
    def __init__(self):
        self.file_manager = FileManager()
        # Creating the main window
        self.window = tk.Tk()
        self.style = ttk.Style()
        # Create variables to store selected values
        self.device_var = tk.StringVar()
        self.tv_var = tk.StringVar()
        self.result_var = tk.StringVar()
        # Variable for radio buttons
        self.type_var = tk.StringVar(value="STB")  # Default value is "STB"
        # Commit entry object
        self.commit_entry = tk.Entry()
        # Result button object
        self.result_button = tk.Button()
        # Repro button object
        self.repro_button = tk.Button()
        # Not Repro button object
        self.not_repro_button = tk.Button()
        # Object for TVs dropdown
        self.tv_dropdown = ttk.Combobox

    # Logic to retrieve data from a link
    def _get_data_from_link(self, url: str) -> dict | str | None:
        """Fetches data from the provided URL

        :param url: url for api request
        :returns: response from request with data of CI build

        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                if 'application/json' in response.headers.get('content-type', ''):
                    return response.json()
                else:
                    return response.json() if response.json() else response.text
            else:
                messagebox.showerror("Error", f"Status Code: {response.status_code}")
                return None
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    def _handle_button_click(self) -> None:
        """Handles the main logic when the Run button is clicked"""
        device, commit_sha, tv_brand = self._get_data_from_ui()
        url = f'https://artifactory.tools.roku.com/artifactory/api/search/prop?CI_JOB_NAME={device}&CI_COMMIT_SHA={commit_sha}'
        data = self._get_data_from_link(url)
        
        if data and 'results' in data:
            try:
                if self.type_var.get() == "TV":
                    selected_uri = [x for x in data['results'] if tv_brand in x['uri']][0]['uri']
                else:
                    selected_uri = data['results'][0]['uri']

                download_data = self._get_data_from_link(selected_uri)
                if download_data and 'downloadUri' in download_data:
                    self.result_var.set(download_data['downloadUri'])
                    self.result_button.config(state="normal", bg="green", fg="white")
                    self.repro_button.config(state="normal")
                    self.not_repro_button.config(state="normal")
                else:
                    messagebox.showinfo("Result", "Download URI not found in the response.")
                    self.result_button.config(state="disabled")
                    self.repro_button.config(state="disabled")
                    self.not_repro_button.config(state="disabled")

            except IndexError:
                messagebox.showinfo("Result", "No matching data found.")
                self.result_button.config(state="disabled")
                self.repro_button.config(state="disabled")
                self.not_repro_button.config(state="disabled")
        else:
            messagebox.showinfo("Result", "No data received from the API.")
            self.result_button.config(state="disabled")
            self.repro_button.config(state="disabled")
            self.not_repro_button.config(state="disabled")

    def _get_data_from_ui(self) -> tuple:
        """Getting data from fields and dropdowns

        :returns: user input data from fields and dropdown
        """
        device = self.device_var.get()  # value of device brand dropdown
        commit_sha = self.commit_entry.get()  # value of commit
        tv_brand = self.tv_var.get()  # value of TV brand dropdown

        return (device, commit_sha, tv_brand)

    def _open_link(self) -> None:
        """Opens the download link in a browser"""
        webbrowser.open(self.result_var.get())

    def _clear_commit_entry(self) -> None:
        """Clears the commit entry field"""
        self.commit_entry.delete(0, tk.END)
        self.result_button.config(state="disabled", bg="#5e5c5d", fg="black")
        self.repro_button.config(state="disabled")
        self.not_repro_button.config(state="disabled")

    def _paste_from_clipboard(self) -> None:
        """Pastes text from the clipboard into the commit entry"""
        try:
            text = self.window.clipboard_get()
            self.commit_entry.delete(0, tk.END)
            self.commit_entry.insert(0, text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _toggle_tv_dropdown(self) -> None:
        """Enables or disables the TV dropdown based on device type"""
        if self.type_var.get() == "TV":
            self.tv_dropdown.config(state="normal")  # or 'readonly' for ttk.Combobox
        else:
            self.tv_dropdown.config(state="disabled")

class DownloaderCI(UserInterfaseActions):
    """Sets up the user interface and actions"""

    STB = (
        'amarillo1080', 'amarillo4k', 'athens', 'austin', 'bandera',
        'benjamin', 'briscoe', 'bryan', 'camden', 'chico', 'cooper',
        'dallas', 'elpasso', 'fruitland4k', 'ftworth', 'gilbert', 'gilbert4k',
        'liberty', 'littlefield', 'logan', 'longview', 'madison', 'malone',
        'marlin', 'miami', 'midland', 'mustang', 'nemo', 'reno', 'rockett',
        'roma', 'sugarland'
    )
    TV_BRAND = (
        'tcl-tcl', 'his-his', 'device2', 'device3', 'device4',
        'device5', 'device6', 'device7'
    )

    def __init__(self) -> None:
        """inialisation UI"""
        super().__init__()
        self.setup_ui()

    def setup_ui(self) -> None:
        """Configure all UI"""
        self._setup_and_run_window()
        self._setup_style()
        self._add_ui_text_of_elements()
        self._add_stb_and_tv_radion_buttons()
        self._add_stb_and_tv_dropdowns()
        self._add_commit_entry()
        self._add_action_buttons()
        self.window.mainloop()

    def _setup_and_run_window(self) -> None:
        """Sets up window"""
        self.window.title("CI downloader beta 0.4.2")
        self.window.geometry("370x250")  # Set window size
        self.window.config(bg="#353535")

    def _setup_style(self) -> None:
        """Sets up style of the window"""
        # Combobox style settings (customization hack for dropdown color)
        self.style.theme_use('clam')  # 'clam' theme allows more flexible style configuration
        self.style.map(
            'CustomCombobox.TCombobox',
            fieldbackground=[('readonly', 'lightblue')],
            selectbackground=[('readonly', 'lightblue')],
            selectforeground=[('readonly', 'darkblue')],
            background=[('readonly', 'lightblue')],
            foreground=[('readonly', 'darkblue')]
        )
        self.style.configure('CustomCombobox.TCombobox', foreground='#dfe6df', fieldbackground='#252525', background='lightblue')

    def _add_ui_text_of_elements(self) -> None:
        """Addding text UI of elements"""
        # UI text for selecting device type
        radio_device_label = tk.Label(self.window, bg="#353535", fg="#dfe6df", text="Device type:")
        radio_device_label.place(x=20, y=10)
        # UI text for selecting device
        device_label = tk.Label(self.window, bg="#353535", fg="#dfe6df", text="Select device:")
        device_label.place(x=130, y=40)
        # UI text for selecting TV brand
        TV_label = tk.Label(self.window, bg="#353535", fg="#dfe6df", text="Select TV brand:")
        TV_label.place(x=130, y=70)
        # UI text for entering the commit
        commit_label = tk.Label(self.window, bg="#353535", fg="#dfe6df", text="Enter Revision link:")
        commit_label.place(x=130, y=100)
        # UI text label for history
        history_label = tk.Label(self.window, bg="#353535", fg="#dfe6df", text="Enter results to history (results.txt):")
        history_label.place(x=20, y=185)

    def _add_stb_and_tv_dropdowns(self) -> None:
        """Adding stb and TV dropdowns"""
        stb_dropdown = ttk.Combobox(self.window, state="normal", width=15, style='CustomCombobox.TCombobox', textvariable=self.device_var)
        stb_dropdown['values'] = self.STB
        stb_dropdown.place(x=235, y=40)

        self.tv_dropdown = ttk.Combobox(self.window, state="disabled", style='CustomCombobox.TCombobox', width=15, textvariable=self.tv_var)
        self.tv_dropdown['values'] = self.TV_BRAND
        self.tv_dropdown.place(x=235, y=70)

    def _add_commit_entry(self) -> None:
        """Adding commit entry field"""
        self.commit_entry = tk.Entry(self.window, bg="#252525", fg="#dfe6df", font=('Arial', 11), width=41)  # Set input field width
        self.commit_entry.place(x=18, y=120)

    def _add_stb_and_tv_radion_buttons(self) -> None:
        """Adding radio buttons for choosing between STB or TV"""
        # Radio buttons for choosing between STB and TV
        stb_radio = tk.Radiobutton(self.window, bg="#353535", fg="#652b8f", text="STB", variable=self.type_var, value="STB",
            command=self._toggle_tv_dropdown)
        stb_radio.place(x=30, y=40)
        stb_radio_spake_label = tk.Label(self.window, bg="#353535", fg="#dfe6df", text="STB")  # Color workaround
        stb_radio_spake_label.place(x=50, y=41)

        tv_radio = tk.Radiobutton(self.window, bg="#353535", fg="#652b8f", text="TV", variable=self.type_var, value="TV",
            command=self._toggle_tv_dropdown)
        tv_radio.place(x=30, y=70)
        tv_radio_spake_label = tk.Label(self.window, bg="#353535", fg="#dfe6df", text="TV")  # Color workaround
        tv_radio_spake_label.place(x=50, y=71)

    def _add_action_buttons(self) -> None:
        """Adding action button for running requests, downloading builds, paste/clear commit entry field,
        buttons for adding test resulsts, and clearing the file with results

        """
        # Button to run the request
        self.run_button = tk.Button(self.window, text="Run", width=10, bg="red", command=self._handle_button_click)
        self.run_button.place(x=270, y=150)

        # Button to clear the commit entry field
        self.clear_button = tk.Button(self.window, bg="#5a2c86", fg="#dfe6df", text="Clear", width=5, command=self._clear_commit_entry)
        self.clear_button.place(x=70, y=150)

        # Button to paste from the clipboard
        self.paste_button = tk.Button(self.window, bg="#5a2c86", fg="#dfe6df", text="Paste", width=5, command=self._paste_from_clipboard)
        self.paste_button.place(x=20, y=150)

        # Button to open the obtained link, initially disabled
        self.result_button = tk.Button(self.window, text="Download", width=8, command=self._open_link, state="disabled", bg="#5e5c5d", fg="black")
        self.result_button.place(x=150, y=150)

        # Button for clearing the file results.txt
        self.paste_button = tk.Button(self.window, bg="#5a2c86", fg="#dfe6df", text="Clear history", width=10,
            command=lambda: self.file_manager.clear_file()
        )
        self.paste_button.place(x=270, y=210)

        # Button Repro for adding into file results.txt
        self.repro_button = tk.Button(self.window, bg="#5a2c86", fg="#ff4747", text="Repro", state="disabled", width=8,
            command=lambda: self.file_manager.append_to_file(self.commit_entry.get() + " - " + self.file_manager.extract_digits(self.result_var.get()) + " Repro")
        )
        self.repro_button.place(x=20, y=210)

        # Button Not Repro for adding into file results.txt
        self.not_repro_button = tk.Button(self.window, bg="#5a2c86", fg="#03fc0b", text="Not Repro", state="disabled", width=8,
            command=lambda: self.file_manager.append_to_file(self.commit_entry.get() + " - " + self.file_manager.extract_digits(self.result_var.get()) + " Not Repro")
        )
        self.not_repro_button.place(x=90, y=210)

if __name__ == "__main__":
    app = DownloaderCI()

