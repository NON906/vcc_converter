#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uvicorn
import httpx
from fastapi import FastAPI, Request, Response

send_url = 'http://127.0.0.1:50021'

app = FastAPI()

@app.get("/presets")
@app.get("/version")
@app.get("/core_versions")
@app.get("/speakers")
@app.get("/speaker_info")
@app.get("/downloadable_libraries")
@app.get("/is_initialized_speaker")
@app.get("/supported_devices")
@app.get("/engine_manifest")
@app.get("/user_dict")
@app.get("/setting")
async def get_default(request: Request):
    requests_client = httpx.AsyncClient()
    response = await requests_client.get(send_url + request.url.path)
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
    response = await requests_client.post(send_url + request.url.path, content=data, params=request.query_params)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

@app.put("/user_dict_word/{word_uuid}")
async def put_user_dict_word(word_uuid: str, request: Request):
    requests_client = httpx.AsyncClient()
    response = await requests_client.put(send_url + request.url.path)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

@app.delete("/user_dict_word/{word_uuid}")
async def delete_user_dict_word(word_uuid: str, request: Request):
    requests_client = httpx.AsyncClient()
    response = await requests_client.delete(send_url + request.url.path)
    result_content = response.content
    result_headers = dict(response.headers)
    result_status_code = response.status_code
    await requests_client.aclose()
    return Response(content=result_content, headers=result_headers, status_code=result_status_code)

if __name__ == "__main__":
    uvicorn.run(app, port=55100)