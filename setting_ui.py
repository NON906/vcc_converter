#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import tkinter as tk
import tkinter.filedialog

from main import load_global_settings

class SettingUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VC Client Converter")

        with open('global.json', 'r', encoding='utf-8') as f:
            self.global_json_dict = json.load(f)

        tk.Label(self, text="* VC Clientのパス").pack(anchor=tk.W)
        self.vcc_exe_file = tk.Entry(self, state='disabled' if self.global_json_dict['vcc_exe_file_embedded'] else 'normal', width=100)
        self.vcc_exe_file.insert(0, self.global_json_dict['vcc_exe_file'])
        self.vcc_exe_file.pack(anchor=tk.W)
        self.vcc_exe_file_button = tk.Button(self, text='開く...', command=self.click_vcc_exe_file_button,
            state='disabled' if self.global_json_dict['vcc_exe_file_embedded'] else 'normal')
        self.vcc_exe_file_button.pack(anchor=tk.E)
        self.vcc_exe_file_embedded = tk.BooleanVar(value=self.global_json_dict['vcc_exe_file_embedded'])
        tk.Checkbutton(self, text='内部でインストールして使用する', variable=self.vcc_exe_file_embedded, command=self.change_vcc_exe_file_embedded).pack(anchor=tk.W)
        tk.Button(self, text='設定を反映', command=self.click_vcc_exe_file_reflect_button).pack(anchor=tk.E)

    def click_vcc_exe_file_button(self):
        file_type = [("実行ファイル", "*.bat;*.exe")]
        default_dir = os.path.dirname(self.vcc_exe_file.get())
        file_name = tk.filedialog.askopenfilename(filetypes=file_type, initialdir=default_dir)
        if len(file_name) > 0:
            self.vcc_exe_file.set(file_name)

    def change_vcc_exe_file_embedded(self):
        if self.vcc_exe_file_embedded.get():
            self.vcc_exe_file.config(state='disabled')
            self.vcc_exe_file_button.config(state='disabled')
        else:
            self.vcc_exe_file.config(state='normal')
            self.vcc_exe_file_button.config(state='normal')

    def click_vcc_exe_file_reflect_button(self):
        self.global_json_dict['vcc_exe_file'] = self.vcc_exe_file.get()
        self.global_json_dict['vcc_exe_file_embedded'] = self.vcc_exe_file_embedded.get()
        with open('global.json', 'w', encoding='utf-8') as f:
            json.dump(self.global_json_dict, f)
        load_global_settings()

if __name__ == "__main__":
    ui = SettingUI()
    ui.mainloop()