import cv2 as cv
import numpy as np
from sklearn import linear_model
from multiprocessing import Value

import psycopg
from pgvector.psycopg import register_vector
from uuid import uuid1

import torch
from torchvision.models import vgg16, VGG16_Weights
from torchvision import transforms
from PIL import Image

image_scale = 0.2


def find_cards(image):
    # TODO image -> []card_img
    pass


# Calculate and return a 2d image with the edges highlighted in white, else black
def detect_edges(img) -> cv.typing.MatLike:
    global image_scale

    img = cv.resize(img, dsize=(9, 0), fx=image_scale, fy=image_scale, interpolation=cv.INTER_CUBIC)
    img_blur = cv.GaussianBlur(img, (3, 3), 0)
    edges = cv.Canny(image=img_blur, threshold1=80, threshold2=80)
    return edges


# This is less precise than ransac, but it is more robust
# It will give us lots of area around the card
def bounding_box_from_edges(edges: cv.typing.MatLike, outlier_percent:int = 1) -> (np.ndarray | None):
    global image_scale

    # Handle the case when there are no edges present
    white_pixels = np.where(edges == 255)
    if len(white_pixels[0]) == 0:
        return None

    # Sort the x and y coordinates
    x_coordinates = white_pixels[1]
    y_coordinates = white_pixels[0]
    sorted_x = np.sort(x_coordinates)
    sorted_y = np.sort(y_coordinates)

    # Calculate the number of outliers to be removed and discard them
    num_outliers = round(outlier_percent / 100 * len(x_coordinates))
    x_without_outliers = sorted_x[num_outliers:-num_outliers]
    y_without_outliers = sorted_y[num_outliers:-num_outliers]

    # Calculate the minimum and maximum coordinates after removing outliers
    min_x = np.min(x_without_outliers) / image_scale
    max_x = np.max(x_without_outliers) / image_scale
    min_y = np.min(y_without_outliers) / image_scale
    max_y = np.max(y_without_outliers) / image_scale

    return np.array([
        (max_x, max_y),
        (max_x, min_y),
        (min_x, max_y),
        (min_x, min_y)
    ])


def corners_from_edges(edges) -> np.ndarray:
    global image_scale
    ransac = linear_model.RANSACRegressor()

    right_col = []
    left_col = []
    bottom_row = []
    top_row = []

    # Find all edges on the right and left of the card
    for i, row in enumerate(edges):
        # Find all white pixel points
        points = [(i, j) for j, pixel in enumerate(row) if pixel > 200]
        if len(points) == 0:
            continue

        # Organise by largest to smallest
        points.sort(key=lambda x: x[1], reverse=True)
        right_col.append(points[0])
        left_col.append(points[-1])

    # Find all edges on the top and bottom of the card
    for j, row in enumerate(edges.T):
        # Find all white pixel points
        points = [(i, j) for i, pixel in enumerate(row) if pixel > 200]
        if len(points) == 0:
            continue

        # Organise by largest to smallest
        points.sort(key=lambda x: x[1], reverse=True)
        top_row.append(points[0])
        bottom_row.append(points[-1])

    # Arrange points for each side
    right_x = np.array([x / image_scale for _, x in right_col]).reshape(-1, 1)
    right_y = np.array([y / image_scale for y, _ in right_col]).reshape(-1, 1)
    left_x = np.array([x / image_scale for _, x in left_col]).reshape(-1, 1)
    left_y = np.array([y / image_scale for y, _ in left_col]).reshape(-1, 1)
    bottom_x = np.array([x / image_scale for _, x in bottom_row]).reshape(-1, 1)
    bottom_y = np.array([y / image_scale for y, _ in bottom_row]).reshape(-1, 1)
    top_x = np.array([x / image_scale for _, x in top_row]).reshape(-1, 1)
    top_y = np.array([y / image_scale for y, _ in top_row]).reshape(-1, 1)

    # Compute ransac for Right edge #
    ransac.fit(right_x, right_y)
    right_coef = ransac.estimator_.coef_
    right_intercept = ransac.estimator_.intercept_

    # Compute ransac for left edge #
    ransac.fit(left_x, left_y)
    left_coef = ransac.estimator_.coef_
    left_intercept = ransac.estimator_.intercept_

    # Compute ransac for bottom edge #
    ransac.fit(bottom_x, bottom_y)
    bottom_coef = ransac.estimator_.coef_
    bottom_intercept = ransac.estimator_.intercept_

    # Compute ransac for top edge #
    ransac.fit(top_x, top_y)
    top_coef = ransac.estimator_.coef_
    top_intercept = ransac.estimator_.intercept_

    # Calculate corner location estimates
    # TODO we need to handle 0 gradient
    top_right_x = (right_intercept - top_intercept) / (top_coef - right_coef)
    top_right_y = top_coef * top_right_x + top_intercept

    top_left_x = (left_intercept - top_intercept) / (top_coef - left_coef)
    top_left_y = top_coef * top_left_x + top_intercept

    bottom_right_x = (right_intercept - bottom_intercept) / (bottom_coef - right_coef)
    bottom_right_y = bottom_coef * bottom_right_x + bottom_intercept

    bottom_left_x = (left_intercept - bottom_intercept) / (bottom_coef - left_coef)
    bottom_left_y = bottom_coef * bottom_left_x + bottom_intercept

    return np.array([
        (round(bottom_right_x.item()), round(bottom_right_y.item())),
        (round(top_right_x.item()), round(top_right_y.item())),
        (round(bottom_left_x.item()), round(bottom_left_y.item())),
        (round(top_left_x.item()), round(top_left_y.item()))
    ])


def create_homography(image: Image) -> Image:

    # Get corners of the card
    np_image = np.array(image)
    edges = detect_edges(np_image)
    pts_src = corners_from_edges(edges)

    # Warp corners into 300x400 image
    H, W, _ = np_image.shape
    pts_dst = np.array([(W, H), (W, 0), (0, H), (0, 0)])
    h, _ = cv.findHomography(pts_src, pts_dst)
    card_homography = cv.warpPerspective(np_image, h, (W, H))
    card_homography = cv.resize(card_homography, (300, 400), card_homography, interpolation=cv.INTER_AREA)
    image = Image.fromarray(card_homography.astype('uint8'), 'RGB')

    return image


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

    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((512, 256), antialias=True),
        transforms.Lambda(crop),
        transforms.Normalize(0.5, 0.5)
    ])

    return model, preprocess, device


def create_feature_vector(homography_img: Image) -> np.ndarray:
    model, preprocess, device = create_model_and_preprocess()
    batch = preprocess(homography_img).unsqueeze(0).to(device)
    features = model(batch).to(device).squeeze(0)
    return features.cpu().detach().numpy().ravel()


def find_closest_cards(config, feature_vector: np.ndarray) -> [str]:
    with psycopg.connect(**config) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM sdk_cache.card ORDER BY features <+> %s LIMIT 5;", (feature_vector,))
            response = cur.fetchall()

            return [card[0] for card in response]


def process_upload(config, image: Image, image_processing_count: Value, user_card_dir: str = "static/user_cards/") -> [str]:
    # TODO potential improvements:
    #   Use text within the image
    #   Compare the features of the top half of the image -> most cards only have images in the top half
    #   Try and get the series of the card

    # Create homography and save that to disc, we can then show this to users in front-end
    image_name = str(uuid1()) + ".png"
    image.save(f"static/user_cards_raw/{image_name}", "PNG")
    homography = create_homography(image)
    homography.save(f"{user_card_dir}{image_name}", "PNG")

    # Calculate features and find close matches
    features = create_feature_vector(homography)
    card_ids = find_closest_cards(config, features)

    # Create db entries
    with psycopg.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute("insert into user_data.upload (image_path) values (%s);", (image_name,))
            cur.execute("select id from user_data.upload where image_path = %s", (image_name,))
            upload_id = cur.fetchone()[0]

            for card_id in card_ids:
                cur.execute("""
                insert into user_data.match (card_id, upload_id) values (%s, %s);
                """, (card_id, upload_id,))

    image_processing_count.value -= 1
