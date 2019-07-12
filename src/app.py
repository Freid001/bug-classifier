from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.schemas import SchemaGenerator
from io import BytesIO
from base64 import b64encode
from base64 import b64decode
from pathlib import Path
from fastai.vision import (
    open_image,
    load_learner,
)

import sys
import uvicorn
import aiohttp
import yaml
import logging
import base64

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
                "classified": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "probability": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    }
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
        },
        "ImageData": {
            "type": "object",
            "properties": {
                "image_data": {
                    "type": "string"
                }
            }
        }
    }
})

app = Starlette()

# load statics
app.mount('/statics', StaticFiles(directory=str(path)+'/statics'), name='statics')

# load html templates
templates = Jinja2Templates(directory=str(path)+'/templates')

# load exported learner => (bug.pkl, bug-multi.pkl)
learner = load_learner(str(path)+'/../exports', 'bug-multi.pkl')

async def get_bytes(url):
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

    logging.info(pred_class)
    logging.info(pred_idx.tolist())

    classified = []
    probability = []
    if not isinstance(pred_class.obj, str):
        classified = pred_class.obj

        for pred, output in zip(pred_idx.tolist(), outputs.tolist()):
            if pred == 1.0:
                probability.append(output)
    else:
        classified.append(pred_class.obj)
        probability.append(outputs[pred_idx].item())

    return {
        "classified": classified,
        "probability": probability
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

@app.route("/api/classify", methods=["POST"])
async def classify_binary(request):
    """
    summary: 'Classify an base64 image.'
    requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/schemas/ImageData'
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

    json = await request.json()
    if 'image_data' in json:
        try:
            return JSONResponse(predict_image_from_bytes(b64decode(json['image_data'])), 200)
        except:
            errors.append({
                "message": "Error reading file."
            })
    else:
        errors.append({
            "message": "Required key: image_data."
        })

    return JSONResponse({
        "errors": errors
    }, 400)

@app.route("/upload", methods=["GET"], include_in_schema=False)
def upload(request):
    return templates.TemplateResponse('upload.html', {'request': request})

@app.route("/upload", methods=["POST"], include_in_schema=False)
async def upload(request):
    errors.clear()
    context = {'request': request}

    try:
        data = await request.form()
        bytes = await (data["file"].read())
        context.update({'image': b64encode(bytes).decode('utf8')})
        context.update({'prediction': predict_image_from_bytes(bytes)})
    except:
        errors.append({
            "message": "Error reading file."
        })

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
