from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
from io import BytesIO
import base64
from glob import glob
import random

from fastai import *
from fastai.vision import *

model_file_url = 'https://www.dropbox.com/s/cbckc70gubbj2m4/Final%20Good%20Model-50%20epochs.pth?raw=1'
model_file_name = 'model'
classes = ['Calls', 'Mastication', 'Nothing']
path = Path(__file__).parent

app = Starlette(debug=True)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

def download_image(img_url, output_name):
    response = requests.get(img_url, stream=True)
    if not response.ok:
        raise Exception("Could not download file: {}".format(response.reason))

    chunksize = 120

    with open(output_name, "wb") as out_file:
        for chunk in response.iter_content(chunk_size=chunksize):
            out_file.write(chunk)

def get_image_name(img_url):
    fields = img_url.split("/")
    if not fields:
        raise Exception("Wrong or unknown url format")
    if not fields[-1] or fields[-1].count(".") == 0:
        raise Exception("Unknown image iname")

    return fields[-1]

async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

async def setup_learner():
    await download_file(model_file_url, path/'models'/f'{model_file_name}.pth')
    data_bunch = ImageDataBunch.single_from_classes(path, classes, size=(100,180)).normalize(imagenet_stats)
    #data_bunch = ImageDataBunch.single_from_classes(path, classes,
        #ds_tfms=get_transforms(), size=(100,180).normalize(imagenet_stats)
    #learn = create_cnn(data_bunch, models.resnet50, pretrained=False)
    learn = cnn_learner(data_bunch, models.resnet50, pretrained=False)
    learn.load(model_file_name)
    return learn

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())

@app.route('/select_random_image', methods=['POST'])
async def select_random_image(request):
    image_files = list(Path('app/images').glob('*'))
    if not image_files:
        return JSONResponse({
            'result': 301,
            'msg': 'No files found'
        })

    random_image = str(random.choice(image_files))
    img_data = None

    with open(str(Path(random_image).absolute()), 'rb') as f:
        img_data = f.read()
   
    img = open_image(BytesIO(img_data))

    return JSONResponse({
        'result': str(learn.predict(img)[0]),
        'img_b64': base64.b64encode(img_data).decode('utf-8')
    })

@app.route('/fetch_analyze', methods=['POST'])
async def fetch_analyze(request):
    data = await request.form()
    # Create folder where images will be stored
    store_dir = 'img_store'
    if not Path(store_dir).exists():
        Path(store_dir).mkdir()

    output_image = get_image_name(data['url'])
    dest_path = str(Path(store_dir).joinpath(output_image).absolute())
    download_image(data['url'], dest_path)

    img_data = None
    with open(dest_path, 'rb') as f:
        img_data = f.read()

    img = open_image(BytesIO(img_data))
    return JSONResponse({
        'result': str(learn.predict(img)[0]),
        'img_b64': base64.b64encode(img_data).decode('utf-8')
    })

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    return JSONResponse({'result': str(learn.predict(img)[0])})

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app, debug=True, host='0.0.0.0', port=8080)
