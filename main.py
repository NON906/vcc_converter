#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import copy
import uvicorn
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

send_url = 'http://127.0.0.1'
send_port = 50021

app = FastAPI()

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

@app.get("/presets")
@app.get("/version")
@app.get("/core_versions")
@app.get("/downloadable_libraries")
@app.get("/is_initialized_speaker")
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

@app.post("/audio_query")
@app.post("/audio_query_from_preset")
@app.post("/accent_phrases")
@app.post("/mora_data")
@app.post("/mora_length")
@app.post("/mora_pitch")
@app.post("/synthesis")
@app.post("/cancellable_synthesis")
@app.post("/multi_synthesis")
@app.post("/morphable_targets")
@app.post("/synthesis_morphing")
@app.post("/connect_waves")
@app.post("/add_preset")
@app.post("/update_preset")
@app.post("/delete_preset")
@app.post("/initialize_speaker")
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
    uvicorn.run(app, port=55100)