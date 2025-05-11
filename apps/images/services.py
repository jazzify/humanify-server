import logging
import uuid
from concurrent import futures as cfutures

from django.conf import settings
from PIL import Image as PImage
from PIL import ImageFilter

from apps.images.constants import ImageTransformations

logger = logging.getLogger(__name__)


def create_processed_media_folder_structure(
    root_folder: str, parent_folder: str
) -> None:
    root_folder_path = f"{settings.MEDIA_ROOT}/processed/{root_folder}"
    if not settings.MEDIA_ROOT.joinpath(root_folder_path).exists():
        settings.MEDIA_ROOT.joinpath(root_folder_path).mkdir()

    parent_folder_path = (
        f"{settings.MEDIA_ROOT}/processed/{root_folder}/{parent_folder}"
    )
    if not settings.MEDIA_ROOT.joinpath(parent_folder_path).exists():
        settings.MEDIA_ROOT.joinpath(parent_folder_path).mkdir()

    for process in ImageTransformations:
        process_path = (
            f"{settings.MEDIA_ROOT}/processed/{root_folder}/{parent_folder}/{process}"
        )
        if not settings.MEDIA_ROOT.joinpath(process_path).exists():
            settings.MEDIA_ROOT.joinpath(process_path).mkdir()


def image_apply_generators(
    image_path: str, root_folder: str, parent_folder: str
) -> None:
    logger.info(f"Processing image: {image_path}")
    create_processed_media_folder_structure(root_folder, parent_folder)

    image_path_thumbnail = image_outfile_name(
        ImageTransformations.THUMBNAIL, root_folder, parent_folder
    )
    image_path_blur = image_outfile_name(
        ImageTransformations.BLUR, root_folder, parent_folder
    )
    image_path_bw = image_outfile_name(
        ImageTransformations.BLACK_AND_WHITE, root_folder, parent_folder
    )
    try:
        with cfutures.ProcessPoolExecutor(max_workers=5) as executor, PImage.open(
            image_path
        ) as img:
            image_copy = img.copy()
            futures = [
                executor.submit(
                    image_generate_thumbnail, image_copy, image_path_thumbnail
                ),
                executor.submit(image_generate_blur, image_copy, image_path_blur),
                executor.submit(
                    image_generate_black_and_white, image_copy, image_path_bw
                ),
            ]
            cfutures.wait(futures)
            logger.info(f"{[future.result() for future in futures]}")
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise e


def image_outfile_name(
    process: ImageTransformations,
    root_folder: str,
    parent_folder: str,
    file_ext: str = "png",
) -> str:
    return f"{settings.MEDIA_ROOT}/processed/{root_folder}/{parent_folder}/{process}/{uuid.uuid4()}.{file_ext}"


def image_generate_thumbnail(img: PImage.Image, file_name: str) -> str:
    img.thumbnail((128, 128))
    img.save(file_name)
    logger.info(f"Generated thumbnail: {file_name}")
    return file_name


def image_generate_blur(img: PImage.Image, file_name: str) -> str:
    new_img = img.filter(ImageFilter.BLUR)
    new_img.save(file_name)
    logger.info(f"Generated blur: {file_name}")
    return file_name


def image_generate_black_and_white(img: PImage.Image, file_name: str) -> str:
    new_img = img.convert("L")
    new_img.save(file_name)
    logger.info(f"Generated B&W: {file_name}")
    return file_name
