from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import Optional
from PIL import Image
import torchvision.transforms as transforms
import torch
from models.tag2text import tag2text_caption
import io
import requests
import traceback

app = FastAPI()


class Model:
    def __init__(self):
        self.model = None
        self.transform = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def load_model(self):
        delete_tag_index = [127, 2961, 3351, 3265, 3338, 3355, 3359]
        self.model = tag2text_caption(pretrained='pretrained/tag2text_swin_14m.pth',
                                      image_size=384,
                                      vit='swin_b',
                                      delete_tag_index=delete_tag_index)
        self.model.threshold = 0.68  # threshold for tagging
        self.model.eval()
        self.model = self.model.to(self.device)

        self.transform = transforms.Compose([
            transforms.Resize((384, 384)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])


model_holder = Model()


@app.on_event("startup")
def startup_event():
    model_holder.load_model()


def inference(image, model, input_tag="None"):
    with torch.no_grad():
        caption, tag_predict = model.generate(image,
                                              tag_input=None,
                                              max_length=50,
                                              return_tag_predict=True)

    if input_tag == '' or input_tag == 'none' or input_tag == 'None':
        return tag_predict[0], None, caption[0]

    # If user input specified tags:
    else:
        input_tag_list = [input_tag.replace(',', ' | ')]

        with torch.no_grad():
            caption, input_tag = model.generate(image,
                                                tag_input=input_tag_list,
                                                max_length=50,
                                                return_tag_predict=True)

        return tag_predict[0], input_tag[0], caption[0]


@app.post("/img2text/")
async def tag2text(file: Optional[UploadFile] = File(None), image_url: Optional[str] = None,
                   specified_tags: Optional[str] = 'None'):
    try:
        if file:
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data)).convert("RGB").resize((384, 384))


        elif image_url:
            response = requests.get(image_url)
            response.raise_for_status()

            image_data = response.content
            image = Image.open(io.BytesIO(image_data)).convert("RGB").resize((384, 384))

        else:
            raise HTTPException(status_code=400, detail="No image provided")

        image = model_holder.transform(image).unsqueeze(0).to(model_holder.device)

        res = inference(image, model_holder.model, specified_tags)

        return {"Model Identified Tags": res[0],
                "User Specified Tags": res[1],
                "Image Caption": res[2]}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}
