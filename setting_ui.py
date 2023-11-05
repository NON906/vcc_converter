#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import threading
import uuid
import tkinter as tk
import tkinter.filedialog
import tkinter.ttk as ttk
import httpx

from main import load_global_settings

class SettingUI(tk.Tk):
    engine_ports = [50021, 50025, 49973, 49540]
    speakers_client = None

    def __init__(self):
        super().__init__()
        self.title("VC Client Converter")

        with open('global.json', 'r', encoding='utf-8') as f:
            self.global_json_dict = json.load(f)
        with open('speakers.json', 'r', encoding='utf-8') as f:
            self.speakers_json_dict = json.load(f)

        tk.Label(self, text="* VC Clientのパス").pack(anchor=tk.W)
        self.vcc_exe_file = tk.Entry(self, state='disabled' if self.global_json_dict['vcc_exe_file_embedded'] else 'normal', width=80)
        self.vcc_exe_file.insert(0, self.global_json_dict['vcc_exe_file'])
        self.vcc_exe_file.pack(anchor=tk.W)
        self.vcc_exe_file_button = tk.Button(self, text='開く...', command=self.click_vcc_exe_file_button,
            state='disabled' if self.global_json_dict['vcc_exe_file_embedded'] else 'normal')
        self.vcc_exe_file_button.pack(anchor=tk.E)
        self.vcc_exe_file_embedded = tk.BooleanVar(value=self.global_json_dict['vcc_exe_file_embedded'])
        #tk.Checkbutton(self, text='内部でインストールして使用する', variable=self.vcc_exe_file_embedded, command=self.change_vcc_exe_file_embedded).pack(anchor=tk.W)
        tk.Button(self, text='設定を反映', command=self.click_vcc_exe_file_reflect_button).pack(anchor=tk.E)

        tk.Label(self, text="* 話者の設定").pack(anchor=tk.W)
        tk.Label(self, text="話者：").pack(anchor=tk.W)
        speakers = self.speakers_combobox_list()
        self.speakers_combobox = ttk.Combobox(self, values=speakers, width=80, state="readonly")
        self.speakers_combobox.current(len(speakers) - 1)
        self.speakers_combobox.bind('<<ComboboxSelected>>', self.change_speakers_combobox)
        self.speakers_combobox.pack(anchor=tk.W)
        tk.Label(self, text="名前：").pack(anchor=tk.W)
        self.speakers_name = tk.Entry(self, width=80)
        self.speakers_name.pack(anchor=tk.W)
        tk.Label(self, text="VOICEVOXエンジン側の対象：").pack(anchor=tk.W)
        engines = ['VOICEVOX（ポート：50021）', 'SHAREVOX（ポート：50025）', 'LMROID（ポート：49973）', 'ITVOICE（ポート：49540）', 'その他（ポート番号を指定）']
        self.engines_combobox = ttk.Combobox(self, values=engines, width=80, state="readonly")
        self.engines_combobox.current(0)
        self.engines_combobox.bind('<<ComboboxSelected>>', self.change_engines_combobox)
        self.engines_combobox.pack(anchor=tk.W)
        self.engine_port = tk.StringVar()
        self.engine_port.trace('w', self.change_engine_port)
        self.engine_port_entry = tk.Entry(self, width=80, state='disabled', textvariable=self.engine_port)
        self.engine_port_entry.pack(anchor=tk.W)
        vv_speakers = self.vv_speakers_list()
        self.vv_speakers_combobox = ttk.Combobox(self, values=vv_speakers, width=80, state="readonly")
        self.vv_speakers_combobox.current(0)
        self.vv_speakers_combobox.pack(anchor=tk.W)
        tk.Button(self, text='追加/更新', command=self.click_speakers_reflect_button).pack(anchor=tk.E)
        tk.Button(self, text='削除', command=self.click_speakers_delete_button).pack(anchor=tk.E)

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

    def speakers_combobox_list(self):
        speakers = []
        for speaker in self.speakers_json_dict:
            speakers.append(speaker['name'])
        speakers.append('（新規追加）')
        return speakers

    def change_speakers_combobox(self, arg):
        current = self.speakers_combobox.current()
        if len(self.speakers_json_dict) > current:
            self.speakers_name.delete(0, tk.END)
            self.speakers_name.insert(0, self.speakers_json_dict[current]['name'])
            port = self.speakers_json_dict[current]['vv_port']
            port_in_list = False
            for loop, engine_port in enumerate(self.engine_ports):
                if engine_port == port:
                    self.engines_combobox.current(loop)
                    port_in_list = True
                    break
            if not port_in_list:
                self.engines_combobox.current(len(self.engine_ports))
                self.engine_port_entry.delete(0, tk.END)
                self.engine_port_entry.insert(0, str(port))
            vv_speakers = self.vv_speakers_list()
            self.vv_speakers_combobox.config(values=vv_speakers)
            for loop, vv_speaker_uuid in enumerate(self.vv_speakers_uuid):
                if vv_speaker_uuid == self.speakers_json_dict[current]['vv_speaker_uuid']:
                    self.vv_speakers_combobox.current(loop)
        else:
            self.speakers_name.delete(0, tk.END)
            vv_speakers = self.vv_speakers_list()
            self.vv_speakers_combobox.config(values=vv_speakers)
            self.vv_speakers_combobox.current(0)

    def change_engines_combobox(self, arg):
        current = self.engines_combobox.current()
        if len(self.engine_ports) > current:
            self.engine_port_entry.config(state='disabled')
        else:
            self.engine_port_entry.config(state='normal')
        self.vv_speakers_combobox.config(values=self.vv_speakers_list())
        self.vv_speakers_combobox.current(0)

    def change_engine_port(self, *args):
        def thread_func():
            try:
                self.vv_speakers_combobox.config(values=self.vv_speakers_list())
                self.vv_speakers_combobox.current(0)
            except:
                pass
        if self.speakers_client is not None:
            self.speakers_client.close()
            self.speakers_client = None
        change_engine_port_thread = threading.Thread(target=thread_func)
        change_engine_port_thread.start()

    def vv_speakers_list(self):
        current = self.engines_combobox.current()
        if len(self.engine_ports) > current:
            port = self.engine_ports[current]
        else:
            port = self.engine_port.get()
        self.speakers_client = httpx.Client()
        try:
            response = self.speakers_client.get(self.global_json_dict['url'] + ':' + str(port) + '/speakers', timeout=httpx.Timeout(5.0, connect=1.0))
            vv_speakers_json = response.json()
        except:
            self.speakers_client.close()
            self.speakers_client = None
            self.vv_speakers_uuid = []
            return ['']
        self.speakers_client.close()
        self.speakers_client = None

        self.vv_speakers_uuid = []
        ret = []
        for vv_speaker in vv_speakers_json:
            self.vv_speakers_uuid.append(vv_speaker['speaker_uuid'])
            ret.append(vv_speaker['name'])
        return ret

    def click_speakers_reflect_button(self):
        if len(self.vv_speakers_uuid) == 0 or self.speakers_name.get() == '':
            return

        current = self.speakers_combobox.current()
        if len(self.speakers_json_dict) == current:
            self.speakers_json_dict.append({})
            self.speakers_json_dict[current]['uuid'] = str(uuid.uuid4())
        self.speakers_json_dict[current]['name'] = self.speakers_name.get()
        engine_current = self.engines_combobox.current()
        if len(self.engine_ports) > engine_current:
            self.speakers_json_dict[current]['vv_port'] = self.engine_ports[engine_current]
        else:
            self.speakers_json_dict[current]['vv_port'] = self.engine_port.get()
        self.speakers_json_dict[current]['vv_speaker_uuid'] = self.vv_speakers_uuid[self.vv_speakers_combobox.current()]
        self.speakers_json_dict[current]['vcc_id'] = -1

        with open('speakers.json', 'w', encoding='utf-8') as f:
            json.dump(self.speakers_json_dict, f)

        self.speakers_combobox.config(values=self.speakers_combobox_list())
        self.speakers_combobox.current(current)

    def click_speakers_delete_button(self):
        current = self.speakers_combobox.current()
        if len(self.speakers_json_dict) <= current:
            return

        del self.speakers_json_dict[current]
        
        with open('speakers.json', 'w', encoding='utf-8') as f:
            json.dump(self.speakers_json_dict, f)

        speakers = self.speakers_combobox_list()
        self.speakers_combobox.config(values=speakers)
        self.speakers_combobox.current(len(speakers) - 1)

if __name__ == "__main__":
    ui = SettingUI()
    ui.mainloop()