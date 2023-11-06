#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import shutil
import json
import re
import httpx

if __name__ == "__main__":
    subprocess.run(['pyinstaller', 'main.py', '--onefile'])

    with open('dist/global.json', 'w', encoding='utf-8') as f:
        f.write('{"url": "http://127.0.0.1", "vcc_port": 18888, "vcc_exe_file_embedded": false, "vcc_exe_file": ""}')

    with open('engine_manifest.json', 'r', encoding='utf-8') as f:
        manifest_json = json.load(f)
    manifest_json['command'] = 'main'
    with open('dist/engine_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest_json, f)

    os.makedirs('dist/engine_manifest_assets', exist_ok=True)

    shutil.copy('engine_manifest_assets/icon.png', 'dist/engine_manifest_assets/icon.png')
    shutil.copy('engine_manifest_assets/update_infos.json', 'dist/engine_manifest_assets/update_infos.json')

    terms_license = subprocess.run(['pip-licenses', '--from=mixed', '--format=markdown', '--with-urls'], capture_output=True).stdout.decode().replace('\r\n', '\n')
    terms_license = re.sub('\\| pyinstaller.*\\|\n', '', terms_license)
    terms_license = re.sub('\\| pyinstaller-hooks-contrib.*\\|\n', '', terms_license)
    with open('engine_manifest_assets/terms_of_service.md', 'w', encoding='utf-8') as f:
        f.write('本プラグインは以下のライブラリおよびPython(v3.12.0, Python Software Foundation License)を使用しています。  \nそれ以外（本プラグイン本体）はMITライセンスに準拠します。\n\n')
        f.write(terms_license)
    shutil.copy('engine_manifest_assets/terms_of_service.md', 'dist/engine_manifest_assets/terms_of_service.md')

    python_response = httpx.get('https://raw.githubusercontent.com/python/cpython/v3.12.0/LICENSE')
    python_license = str(python_response.content)
    python_response.close()
    dependency_license = subprocess.run(['pip-licenses', '--from=mixed', '--format=json', '--with-urls', '--with-license-file', '--no-license-path'], capture_output=True).stdout.decode()
    input_json = json.loads(dependency_license)
    output_json = [{
        'name': 'python',
        'version': '3.12.0',
        'license': 'Python Software Foundation License',
        'text': python_license
    }]
    for input_item in input_json:
        if input_item['Name'] == 'pyinstaller' or input_item['Name'] == 'pyinstaller-hooks-contrib':
            continue
        output_item = {
            'name': input_item['Name'],
            'version': input_item['Version'],
            'license': input_item['License'],
            'text': input_item['LicenseText']
        }
        output_json.append(output_item)
    with open('engine_manifest_assets/dependency_licenses.json', 'w', encoding='utf-8') as f:
        json.dump(output_json, f)
    shutil.copy('engine_manifest_assets/dependency_licenses.json', 'dist/engine_manifest_assets/dependency_licenses.json')

    shutil.make_archive('vcc_converter', format='zip', root_dir='dist')
    if os.path.isfile('vcc_converter_vX.X.X_win.vvpp'):
        os.remove('vcc_converter_vX.X.X_win.vvpp')
    os.rename('vcc_converter.zip', 'vcc_converter_vX.X.X_win.vvpp')