from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.schemas import SchemaGenerator
from io import BytesIO
from pathlib import Path
from base64 import b64encode
from fastai.vision import (
    open_image,
    load_learner,
)

import sys
import uvicorn
import aiohttp
import yaml
import logging

path = Path(__file__).parent
errors = []

# define open api schemas
schemas = SchemaGenerator({
    "openapi": "3.0.0",
    "info": {
        "title": "App",
        "version": "1.0"
    },
    "servers": [{
        "url": "http://localhost:{port}",
        "variables": {
            "port": {
                "default": "8000"
            }
        }
    }],
    "schemas": {
        "Classify": {
            "type": "object",
            "properties": {
                "class": {
                    "type": "string"
                },
                "probability": {
                    "type": "integer"
                }
            }
        },
        "ErrorMessage": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string"
                }
            }
        },
        "Errors": {
            "type": "array",
            "items": {
                "$ref": "#/schemas/ErrorMessage"
            }
        }
    }
})

app = Starlette()

# load statics
app.mount('/statics', StaticFiles(directory=str(path)+'/statics'), name='statics')

# load html templates
templates = Jinja2Templates(directory=str(path)+'/templates')

# load exported learner
learner = load_learner(str(path)+'/../exports', 'bug.pkl')

async def get_bytes(url):
    logging.info(url)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.content_type in [
                    "image/png",
                    "image/jpeg",
                    "image/gif"
                ]:
                    return await response.read()
                else:
                    errors.append({
                        "message": "Invalid mime type, expects: image/png, image/jpeg or image/gif."
                    })
                    return False
    except:
        errors.append({
            "message": "Invalid url."
        })
        return False

def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    pred_class, pred_idx, outputs = learner.predict(img)

    return {
        "class": pred_class.obj,
        "probability": outputs[pred_idx].item()
    }

@app.route("/api/classify", methods=["GET"])
async def classify_url(request):
    """
    summary: 'Classify an image by url.'
    parameters:
    - name: 'url'
      description: 'Url of image.'
      in: 'query'
      schema:
        type: 'string'
      required: true
    responses:
        200:
            description: 'ok'
            content:
                application/json:
                  schema:
                    $ref: '#/schemas/Classify'
        400:
            description: 'bad request'
            content:
                application/json:
                  schema:
                    $ref: '#/schemas/Errors'
    """
    errors.clear()
    if 'url' in request.query_params:
        bytes = await get_bytes(request.query_params['url'])
        if bytes is not False:
            return JSONResponse(predict_image_from_bytes(bytes), 200)
    else:
        errors.append({
            "message": "Url is required."
        })

    return JSONResponse({
        "errors": errors
    }, 400)

# @app.route("/api/classify", methods=["POST"])
# async def classify_url(request):
#     """
#     summary: 'Classify an image binary.'
#     responses:
#         200:
#             description: 'ok'
#             content:
#                 application/json:
#                   schema:
#                     $ref: '#/schemas/Classify'
#         400:
#             description: 'bad request'
#             content:
#                 application/json:
#                   schema:
#                     $ref: '#/schemas/Errors'
#     """
#     errors.clear()
#     if 'url' in request.body.:
#         bytes = await get_bytes(request.query_params['url'])
#         if bytes is not False:
#             return JSONResponse(predict_image_from_bytes(bytes), 200)
#     else:
#         errors.append({
#             "message": "Url is required."
#         })
#
#     return JSONResponse({
#         "errors": errors
#     }, 400)

@app.route("/upload", methods=["GET"], include_in_schema=False)
def upload(request):
    return templates.TemplateResponse('upload.html', {'request': request})

@app.route("/upload", methods=["POST"], include_in_schema=False)
async def upload(request):
    errors.clear()
    context = {'request': request}

    # try:
    data = await request.form()

    logging.info(data)

    bytes = await (data["file"].read())
    context.update({'image': b64encode(bytes).decode('utf8')})
    context.update({'prediction': predict_image_from_bytes(bytes)})
    # except:
    #     errors.append({
    #         "message": "Error reading file."
    #     })

    # logging.info(bytes)
    # logging.info(b64encode(bytes).decode('utf8'))

    return templates.TemplateResponse('upload.html', context)

@app.route("/url", methods=["GET"], include_in_schema=False)
async def url(request):
    errors.clear()
    context = {'request': request}

    if 'url' in request.query_params:
        context.update({'url': request.query_params['url']})

        bytes = await get_bytes(context.get('url'))
        if bytes is not False:
            context.update({'prediction': predict_image_from_bytes(bytes)})

    context.update({'errors': errors})

    return templates.TemplateResponse('url.html', context)

@app.route("/", methods=["GET"], include_in_schema=False)
def upload(request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.route("/api/schema", methods=["GET"], include_in_schema=False)
def openapi_schema(request):
    return JSONResponse(schemas.get_schema(routes=app.routes))

if __name__ == '__main__':
    assert sys.argv[-1] in ("server", "schema"), "Usage: app.py [server|schema]"

    if sys.argv[-1] == "server":
        uvicorn.run(app, host="0.0.0.0", port=8000)

    elif sys.argv[-1] == "schema":
        schema = schemas.get_schema(routes=app.routes)
        print(yaml.dump(schema, default_flow_style=False))