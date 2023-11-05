#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import copy
import argparse
import os
import subprocess
import wave
import base64
import shutil
import threading
from io import BytesIO
import uvicorn
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import setting_ui

send_url = 'http://127.0.0.1'
send_port = 50021
vcc_url = 'http://127.0.0.1:18888'
vcc_exe_file = r""
timestamp = 0
setting_ui_obj = None

def load_global_settings():
    global send_url
    global vcc_url
    global vcc_exe_file
    with open('global.json', 'r', encoding='utf-8') as f:
        json_dict = json.load(f)
    send_url = json_dict['url']
    vcc_url = json_dict['url'] + ':' + str(json_dict['vcc_port'])
    if json_dict['vcc_exe_file_embedded']:
        vcc_exe_file = 'bin/MMVCServerSIO/start_http.bat'
    else:
        vcc_exe_file = json_dict['vcc_exe_file']

load_global_settings()

app = FastAPI()

def open_setting_ui():
    global setting_ui_obj
    if setting_ui_obj is None:
        def thread_func():
            setting_ui_obj = setting_ui.SettingUI()
            setting_ui_obj.mainloop()
            setting_ui_obj = None
        thread = threading.Thread(target=thread_func)
        thread.start()

async def check_voice_changer():
    try:
        requests_client = httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=1.0))
        res = await requests_client.get(vcc_url + '/api/hello')
        ret = res.status_code == 200
        await requests_client.aclose()
        return ret
    except:
        return False

async def launch_voice_changer():
    global timestamp

    current_path = os.getcwd()
    os.chdir(os.path.dirname(vcc_exe_file))
    subprocess.Popen(os.path.basename(vcc_exe_file))
    os.chdir(current_path)

    while not await check_voice_changer():
        pass

    requests_client = httpx.AsyncClient()
    json_data = {
        'timestamp': timestamp,
        'buffer': base64.b64encode(bytes(48000 * 2)).decode("utf-8")
    }
    timestamp += 1
    await requests_client.post(vcc_url + '/test', content=json.dumps(json_data))
    await requests_client.aclose()

@app.post("/change_target_port")
async def post_change_target_port(port: int):
    send_port = port

@app.get("/speakers")
async def get_speakers():
    with open('speakers.json', 'r', encoding='utf-8') as f:
        speakers_json = json.load(f)

    vv_speakers_json_dict = {}
    for speaker in speakers_json:
        port = speaker["vv_port"]
        if not str(port) in vv_speakers_json_dict:
            requests_client = httpx.AsyncClient()
            response = await requests_client.get(send_url + ':' + str(port) + '/speakers')
            vv_speakers_json_dict[str(port)] = response.json()
            await requests_client.aclose()

    ret = []
    style_count = 0
    for speaker in speakers_json:
        for vv_speaker in vv_speakers_json_dict[str(speaker["vv_port"])]:
            if vv_speaker["speaker_uuid"] == speaker["vv_speaker_uuid"]:
                new_speaker = copy.deepcopy(vv_speaker)
                new_speaker["speaker_uuid"] = speaker["uuid"]
                new_speaker["name"] = speaker["name"]
                for style in new_speaker["styles"]:
                    style["id"] = style_count
                    style_count += 1
                ret.append(new_speaker)
                break

    return ret

@app.get("/speaker_info")
async def get_speaker_info(speaker_uuid: str, core_version: str | None = None):
    with open('speakers.json', 'r', encoding='utf-8') as f:
        speakers_json = json.load(f)

    for speaker in speakers_json:
        if speaker["uuid"] == speaker_uuid:
            requests_client = httpx.AsyncClient()
            if core_version is not None:
                response = await requests_client.get(send_url + ':' + str(speaker["vv_port"]) + '/speaker_info', params={
                    "speaker_uuid": speaker["vv_speaker_uuid"],
                    "core_version": core_version
                    })
            else:
                response = await requests_client.get(send_url + ':' + str(speaker["vv_port"]) + '/speaker_info', params={
                    "speaker_uuid": speaker["vv_speaker_uuid"]
                    })
            result_content = response.content
            await requests_client.aclose()
            send_port = speaker["vv_port"]
            return Response(content=result_content, media_type='application/json')
    
    result_content_json = jsonable_encoder({
        "detail": "該当する話者が見つかりません"
    })
    return JSONResponse(content=result_content_json, status_code=404)

async def local_get_speaker(speaker: int):
    with open('speakers.json', 'r', encoding='utf-8') as f:
        speakers_json = json.load(f)

    vv_speakers_json_dict = {}
    for speaker_json in speakers_json:
        port = speaker_json["vv_port"]
        if not str(port) in vv_speakers_json_dict:
            requests_client = httpx.AsyncClient()
            response = await requests_client.get(send_url + ':' + str(port) + '/speakers')
            vv_speakers_json_dict[str(port)] = response.json()
            await requests_client.aclose()

    style_count = 0
    for speaker_json in speakers_json:
        for vv_speaker in vv_speakers_json_dict[str(speaker_json["vv_port"])]:
            if vv_speaker["speaker_uuid"] == speaker_json["vv_speaker_uuid"]:
                if style_count <= speaker and speaker < style_count + len(vv_speaker["styles"]):
                    send_port = speaker_json["vv_port"]
                    return vv_speaker["styles"][speaker - style_count]["id"], speaker_json["vcc_id"]
                style_count += len(vv_speaker["styles"])

    return -1, -1

@app.post("/initialize_speaker")
async def post_initialize_speaker(request: Request):
    open_setting_ui()
    if not await check_voice_changer():
        await launch_voice_changer()
    data: bytes = await request.body()
    params = dict(request.query_params)
    params["speaker"], _ = await local_get_speaker(int(params["speaker"]))
    requests_client = httpx.AsyncClient()
    response = await requests_client.post(send_url + ':' + str(send_port) + '/initialize_speaker', content=data, params=params)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

@app.get("/is_initialized_speaker")
async def get_is_initialized_speaker(request: Request):
    if not await check_voice_changer():
        return Response(content='false', media_type='application/json')
    params = dict(request.query_params)
    params["speaker"], _ = await local_get_speaker(int(params["speaker"]))
    if params["speaker"] < 0:
        return Response(content='false', media_type='application/json')
    requests_client = httpx.AsyncClient()
    response = await requests_client.get(send_url + ':' + str(send_port) + '/is_initialized_speaker', params=params)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

async def vcc_test(wav_content: bytes, vcc_id: int, write_file):
    global timestamp

    if not await check_voice_changer():
        await launch_voice_changer()

    vc_input = b''
    file_in_memory = BytesIO(wav_content)
    with wave.open(file_in_memory, 'rb') as wav_file:
        vc_input += wav_file.readframes(wav_file.getnframes())

    if vcc_id >= 0:
        requests_client = httpx.AsyncClient()
        response = await requests_client.post(vcc_url + '/update_settings', content=json.dumps({'key': 'modelSlotIndex', 'val': vcc_id}))
        await requests_client.aclose()

    requests_client = httpx.AsyncClient()
    json_data = {
        'timestamp': timestamp,
        'buffer': base64.b64encode(vc_input).decode("utf-8")
    }
    timestamp += 1
    response = await requests_client.post(vcc_url + '/test', content=json.dumps(json_data))
    base64_str = response.json()['changedVoiceBase64']
    await requests_client.aclose()
    
    with wave.open(write_file, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(48000)
        wav_file.writeframes(base64.b64decode(base64_str))

@app.post("/synthesis")
@app.post("/cancellable_synthesis")
async def post_synthesis(request: Request):
    data = await request.json()
    params = dict(request.query_params)
    data['outputSamplingRate'] = 48000
    params["speaker"], vcc_id = await local_get_speaker(int(params["speaker"]))
    requests_client = httpx.AsyncClient()
    response = await requests_client.post(send_url + ':' + str(send_port) + request.url.path, content=json.dumps(data), params=params)
    result_content = response.content
    result_status_code = response.status_code
    await requests_client.aclose()

    if result_status_code != 200:
        return Response(content=result_content, media_type='application/json', status_code=result_status_code)

    fileIO = BytesIO()
    await vcc_test(result_content, vcc_id, fileIO)

    return Response(content=fileIO.getvalue(), media_type='audio/wav')

@app.post("/multi_synthesis")
async def post_multi_synthesis(request: Request):
    datas_json = await request.json()
    params = dict(request.query_params)
    vcc_id = int(params["speaker"])
    params["speaker"], vcc_id = await local_get_speaker(int(params["speaker"]))
    os.makedirs('./.temp/dir_zip', exist_ok=True)
    for loop, data in enumerate(datas_json):
        data['outputSamplingRate'] = 48000
        requests_client = httpx.AsyncClient()
        response = await requests_client.post(send_url + ':' + str(send_port) + '/synthesis', content=json.dumps(data), params=params)
        result_content = response.content
        await requests_client.aclose()
        with open('./.temp/dir_zip/%03d.wav' % (loop + 1), 'wb') as f:
            await vcc_test(result_content, vcc_id, f)
    shutil.make_archive('./.temp/multi_synthesis', format='zip', root_dir='./.temp/dir_zip')
    with open('./.temp/multi_synthesis.zip', 'rb') as f:
        ret = f.read()
    shutil.rmtree('./.temp')
    return Response(content=ret, media_type='application/zip')

@app.get("/presets")
@app.get("/version")
@app.get("/core_versions")
@app.get("/downloadable_libraries")
@app.get("/supported_devices")
@app.get("/engine_manifest")
@app.get("/user_dict")
@app.get("/setting")
async def get_default(request: Request):
    requests_client = httpx.AsyncClient()
    response = await requests_client.get(send_url + ':' + str(send_port) + request.url.path, params=request.query_params)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

@app.post("/audio_query_from_preset")
@app.post("/morphable_targets")
@app.post("/synthesis_morphing")
@app.post("/connect_waves")
@app.post("/add_preset")
@app.post("/update_preset")
@app.post("/delete_preset")
@app.post("/user_dict_word")
@app.post("/import_user_dict")
@app.post("/setting")
async def post_default(request: Request):
    data: bytes = await request.body()
    requests_client = httpx.AsyncClient()
    response = await requests_client.post(send_url + ':' + str(send_port) + request.url.path, content=data, params=request.query_params)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

@app.post("/audio_query")
@app.post("/accent_phrases")
@app.post("/mora_data")
@app.post("/mora_length")
@app.post("/mora_pitch")
async def post_default_with_speaker(request: Request):
    data: bytes = await request.body()
    params = dict(request.query_params)
    params["speaker"], _ = await local_get_speaker(int(params["speaker"]))
    requests_client = httpx.AsyncClient()
    response = await requests_client.post(send_url + ':' + str(send_port) + request.url.path, content=data, params=params)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

@app.put("/user_dict_word/{word_uuid}")
async def put_user_dict_word(word_uuid: str, request: Request):
    requests_client = httpx.AsyncClient()
    response = await requests_client.put(send_url + ':' + str(send_port) + request.url.path, params=request.query_params)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

@app.delete("/user_dict_word/{word_uuid}")
async def delete_user_dict_word(word_uuid: str, request: Request):
    requests_client = httpx.AsyncClient()
    response = await requests_client.delete(send_url + ':' + str(send_port) + request.url.path, params=request.query_params)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

if __name__ == "__main__":
    if not os.path.isfile('speakers.json'):
        with open('speakers.json', 'w', encoding='utf-8') as f:
            f.write('[]')
    with open('speakers.json', 'r', encoding='utf-8') as f:
        speakers_json = json.load(f)
    if len(speakers_json) <= 0:
        open_setting_ui()

    uvicorn.run(app, port=55100)