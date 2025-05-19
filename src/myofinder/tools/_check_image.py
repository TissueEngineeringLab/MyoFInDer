# coding: utf-8

from pathlib import Path
from cv2 import imread, cvtColor, IMREAD_ANYCOLOR, IMREAD_GRAYSCALE, \
    IMREAD_COLOR, COLOR_BGR2RGB
from numpy import zeros, stack, concatenate, ndarray
from re import findall
from typing import Optional


def check_image(image_path: Path) -> Optional[ndarray]:
    """Function making sure that the loaded image has 3 channels and is 8-bits.

    It ignores the alpha channel if any, and can handle all the usual dtypes.
    Grayscale images simply receive two additional empty channels to give a
    3-channel image.

    Args:
        image_path: The path to the image to load.

    Returns:
        The loaded image as a 3-channel 8-bits array, or None if the loading
        wasn't successful.
    """

    # Loading the image
    cv_img = imread(str(image_path), IMREAD_ANYCOLOR)

    # In case the file cannot be reached
    if cv_img is None:
        return None

    zero_channel = zeros([cv_img.shape[0], cv_img.shape[1]])

    # In this section, we ensure that the image is RGB
    # The image is grayscale, building a 3 channel image from it
    if len(cv_img.shape) == 2:
        cv_img = stack([concatenate([zero_channel, zero_channel],
                                    axis=2), cv_img], axis=2)

    # If there's an Alpha channel on a grayscale, ignore it
    elif len(cv_img.shape) == 3 and cv_img.shape[2] == 2:
        cv_img = imread(str(image_path), IMREAD_GRAYSCALE)
        cv_img = stack([concatenate([zero_channel, zero_channel],
                                    axis=2), cv_img], axis=2)

    # The image is 3 or 4 channels, ignoring the Alpha channel if any
    elif len(cv_img.shape) == 3 and cv_img.shape[2] in [3, 4]:
        cv_img = imread(str(image_path), IMREAD_COLOR)
        cv_img = cvtColor(cv_img, COLOR_BGR2RGB)

    # If it's another format, returning None to indicate it wasn't successful
    else:
        return None

    # Parsing the d_type string of the image
    try:
        depth = findall(r'\d+', str(cv_img.dtype))[0]
    except IndexError:
        depth = ''
    type_ = str(cv_img.dtype).strip(depth)

    # In this section, we ensure that the image is 8-bits
    # If it's boolean, the image will be black and white
    if type_ == 'bool':
        cv_img = (cv_img.astype('uint8') * 255).astype('uint8')

    # If it's int, first making it uint and then casting to uint8
    elif type_ == 'int':
        cv_img = (cv_img + 2 ** (int(depth) - 1)).astype('uint' +
                                                         depth)
        cv_img = (cv_img / 2 ** (int(depth) - 8)).astype('uint8')

    # If it's uint, simply casting to uint8
    elif type_ == 'uint':
        cv_img = (cv_img / 2 ** (int(depth) - 8)).astype('uint8')

    # If it's float, casting to [0-1] and then to uint8
    elif type_ == 'float':
        cv_img = ((cv_img - cv_img.min()) / (cv_img.max() - cv_img.min())
                  * 255).astype('uint8')

    # If it's another format, returning None to indicate it wasn't successful
    else:
        return None

    return cv_img
