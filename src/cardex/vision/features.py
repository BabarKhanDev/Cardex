from io import BytesIO

import numpy as np
import requests
import torch
from cardex.catalogue.repository import get_all_card_ids_and_urls, set_card_features
from PIL import Image
from torchvision import transforms
from torchvision.models import VGG16_Weights, vgg16


def create_model_and_preprocess():

    # Create Model
    weights = VGG16_Weights.IMAGENET1K_V1
    model = vgg16(weights=weights)
    model.eval()
    model.classifier = model.classifier[0]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # # Built in transforms are a bit weird, they crop the image rather than squeezing it
    # # Create inference transforms
    # preprocess = transforms.Compose([
    #     weights.transforms()
    # ])

    # Create inference transforms
    def crop(image):
        return transforms.functional.crop(image, 0, 0, 256, 256)

    preprocess = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Resize((512, 256), antialias=True),
            transforms.Lambda(crop),
            transforms.Normalize(0.5, 0.5),
        ]
    )

    return model, preprocess, device


def create_feature_vector(homography_img: Image.Image) -> np.ndarray:
    model, preprocess, device = create_model_and_preprocess()
    batch = preprocess(homography_img).unsqueeze(0).to(device)
    features = model(batch).to(device).squeeze(0)
    return features.cpu().detach().numpy().ravel()


def calculate_features_of_all_cards() -> None:

    model, preprocess, device = create_model_and_preprocess()

    card_details = get_all_card_ids_and_urls()
    for card_id, url in card_details:
        response = requests.get(url)
        if response.status_code != 200:
            continue

        image = Image.open(BytesIO(response.content)).convert("RGB")
        batch = preprocess(image).unsqueeze(0).to(device)
        features = model(batch).squeeze(0).cpu().detach().numpy()
        set_card_features(card_id, features)
