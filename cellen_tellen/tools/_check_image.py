# coding: utf-8

from pathlib import Path
from cv2 import imread, cvtColor, IMREAD_ANYCOLOR, IMREAD_GRAYSCALE, \
    IMREAD_COLOR, COLOR_BGR2RGB
from numpy import zeros, stack, concatenate, ndarray
from re import findall
from typing import Optional, Tuple


def check_image(image_path: Path,
                error_path: Optional[Path] = None) -> Tuple[ndarray, ndarray]:
    """Function making sure that the loaded image has 3 channels and is 8-bits.

    It ignores the alpha channel if any, and can handle all the usual dtypes.
    Grayscale images simply receive two additional empty channels to give a
    3-channel image.

    Args:
        image_path: The path to the image to load.
        error_path: The path to the image displaying an error message. If not
            given, an exception is raised instead of returning the error image.

    Returns:
        The loaded image as a 3-channel 8-bits array, and a 1-channel array of
        the same shape containing only zeros.
    """

    # Loading the image
    cv_img = imread(str(image_path), IMREAD_ANYCOLOR)
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

    # Unexpected image format, loading an error message image or raising
    else:
        # Raising exception if asked to
        if error_path is None:
            raise ValueError("Unexpected format, couldn't load the image.")
        cv_img = imread(str(error_path))
        zero_channel = zeros([cv_img.shape[0], cv_img.shape[1]])
        cv_img = cvtColor(cv_img, COLOR_BGR2RGB)

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
        cv_img = ((cv_img - cv_img.min(initial=None)) /
                  (cv_img.max(initial=None) - cv_img.min(initial=None))
                  * 255).astype('uint8')

    # If it's another format; displaying an error image or raising
    else:
        # Raising exception if asked to
        if error_path is None:
            raise ValueError("Unexpected format, couldn't load the image.")
        cv_img = imread(str(error_path))
        zero_channel = zeros([cv_img.shape[0], cv_img.shape[1]])
        cv_img = cvtColor(cv_img, COLOR_BGR2RGB)

    return cv_img, zero_channel
