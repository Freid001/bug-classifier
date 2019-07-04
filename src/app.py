from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from io import BytesIO
from pathlib import Path
from fastai.vision import (
    open_image,
    load_learner,
)

import sys
import uvicorn
import aiohttp
import logging

app = Starlette()
path = Path(__file__).parent
errors = []

# load html templates
templates = Jinja2Templates(directory=str(path)+'/templates')

# load exported learner
learner = load_learner(str(path)+'/../exports', 'bug.pkl')

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

    return JSONResponse({
        "prediction": pred_class.obj,
        "pred_idx": pred_idx,
        "output": outputs[pred_idx].item()
    })

@app.route("/api/classify", methods=["GET"])
async def classify_url(request):
    errors.clear()
    if 'url' in request.query_params:
        bytes = await get_bytes(request.query_params['url'])
        if bytes is not False:
            return predict_image_from_bytes(bytes)
    else:
        errors.append({
            "message": "Url is required."
        })

    return JSONResponse({
        "errors": errors
    })

# @app.route("/api/classify", methods=["POST"])
# async def upload(request):
#     data = await request.form()
#     bytes = await (data["file"].read())
#     return
# predict_image_from_bytes(bytes)

@app.route("/")
def index(request):
    return templates.TemplateResponse('index.html', {'request': request})

if __name__ == "__main__":
    if "server" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8000)

# https://media.wired.com/photos/5bb532b7f8a2e62d0bd5c4e3/master/pass/bee-146810332.jpg
# https://i.cbc.ca/1.3624693.1502504172!/fileImage/httpImage/image.jpg_gen/derivatives/16x9_780/yellow-jacket.jpg
# https://media.mnn.com/assets/images/2016/04/atlas-moth-scale.jpg.838x0_q80.jpg



# https://medium.com/@lankinen/fastai-model-to-production-this-is-how-you-make-web-app-that-use-your-model-57d8999450cf