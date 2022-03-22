# coding: utf-8

from deepcell.applications import Mesmer
import numpy as np
import numpy.ma as ma
from pathlib import Path
import cv2
from typing import List, Tuple, Any, Union

from .tools import check_image

# Table for converting color strings to channels, assuming BGR images
numpy_color_to_int = {"red": 0,
                      "green": 1,
                      "blue": 2}


class Image_segmentation:
    """Class for processing images, detecting fibers and nuclei."""

    def __init__(self) -> None:
        """Simply loads the Mesmer library."""

        self._app = Mesmer()

    def __call__(self,
                 path: Path,
                 nuclei_color: str,
                 fibre_color: str,
                 fibre_threshold: int,
                 small_objects_threshold: int) -> \
            Union[Tuple[List[Tuple[np.ndarray, np.ndarray]],
                  List[Tuple[np.ndarray, np.ndarray]],
                  Tuple[Any], float], Tuple[None, None, None, None]]:
        """Computes the nuclei positions and optionally the fibers positions.

        Also returns whether the nuclei are inside or outside the fibers.

        Args:
            path: The path to the image to process.
            nuclei_color: The color of the nuclei, as a string.
            fibre_color: The color of the fibres, as a string.
            fibre_threshold: The gray level threshold above which a pixel is
                considered to be part of a fiber.
            small_objects_threshold: Objects whose area is lower than this
                value (in pixels) will not be considered.

        Returns:
            The list of nuclei outside the fibres, the list of nuclei inside
            the fibers, the list of fibre contours, and the ratio of fibre area
            over the total area.
        """

        # Converting colors from string to int
        colors = [numpy_color_to_int[nuclei_color],
                  numpy_color_to_int[fibre_color]]

        # Loads the image and keeps only the nuclei and fibres channels
        image = check_image(path)

        # The image couldn't be loaded
        if image is None:
            return None, None, None, None

        two_channel_image = np.array([image[:, :, colors]])

        # Default parameters
        maxima_threshold = 0.05
        maxima_smooth = 0
        interior_threshold = 0.3
        interior_smooth = 2
        fill_holes_threshold = 15
        radius = 2
        microns_per_pixel = None
        batch_size = 8

        # Actual nuclei detection function
        labeled_image = self._app.predict(
            image=two_channel_image,
            batch_size=batch_size,
            image_mpp=microns_per_pixel,
            preprocess_kwargs={},
            compartment='nuclear',
            pad_mode='constant',
            postprocess_kwargs_whole_cell={},
            postprocess_kwargs_nuclear={
                'maxima_threshold': maxima_threshold,
                'maxima_smooth': maxima_smooth,
                'interior_threshold': interior_threshold,
                'interior_smooth': interior_smooth,
                'small_objects_threshold': small_objects_threshold,
                'fill_holes_threshold': fill_holes_threshold,
                'radius': radius})

        # Removing useless axes on the output
        labeled_image = np.squeeze(labeled_image)

        # Getting the fibre mask
        mask = self._get_fibre_mask(image[:, :, colors[1]], fibre_threshold)

        # Calculating the area of fibers over the total area
        area = np.count_nonzero(mask) / mask.shape[0] / mask.shape[1]

        # Finding the contours of the fibers
        mask_8_bits = (mask * 255).astype('uint8')
        fibre_contours, _ = cv2.findContours(mask_8_bits, cv2.RETR_LIST,
                                             cv2.CHAIN_APPROX_SIMPLE)
        fibre_contours = tuple(map(np.squeeze, fibre_contours))

        # Getting the position of the nuclei
        nuclei_out, nuclei_in = self._get_nuclei_positions(labeled_image, mask)

        return nuclei_out, nuclei_in, fibre_contours, area

    @staticmethod
    def _get_fibre_mask(fibre_channel: np.ndarray,
                        threshold: int) -> np.ndarray:
        """Applies several images processing methods to the fibre channel of
        the image to smoothen the outline.

        Args:
            fibre_channel: The channel of the image containing the fibres.
            threshold: The gray level threshold above which a pixel is
                considered to be part of a fiber.

        Returns:
            A boolean mask containing the position of the fibres
        """

        # First, apply a base threshold
        kernel = np.ones((10, 10), np.uint8)
        _, processed = cv2.threshold(fibre_channel, threshold, 255,
                                     cv2.THRESH_BINARY)

        # Opening, to remove noise in the background
        processed = cv2.morphologyEx(processed,
                                     cv2.MORPH_OPEN, kernel)

        # Closing, to remove noise inside the fibres
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)

        # Inverting black and white
        processed = cv2.bitwise_not(processed)

        # Find contours of the holes inside the fibers
        contours, _ = cv2.findContours(processed, cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Fill hole if its area is smaller than 0.5% of the image
            if cv2.contourArea(contour) / \
                    (fibre_channel.shape[0] * fibre_channel.shape[1]) < 5e-3:
                cv2.drawContours(processed, [contour], -1, (0, 0, 0), -1)

        # Inverting black and white again
        processed = cv2.bitwise_not(processed)

        # Creating a boolean mask, later used to generate a masked array
        mask = processed.astype(bool)

        return mask

    @staticmethod
    def _get_nuclei_positions(labeled_image: np.ndarray,
                              mask: np.ndarray,
                              fibre_threshold: float = 0.85) -> \
            Tuple[List[Tuple[np.ndarray, np.ndarray]],
                  List[Tuple[np.ndarray, np.ndarray]]]:
        """Computes the center of the nuclei and determines whether they're
        positive or not.

        Args:
            labeled_image: The image containing the nuclei.
            mask: The boolean mask of the fibers.
            fibre_threshold: Fraction of area above which a nucleus is
                considered to be inside a fiber.

        Returns:
            The list of the centers of nuclei outside of fibers, and the list
            of centers of nuclei inside fibres
        """

        nuclei_out_fibre = []
        nuclei_in_fibre = []

        # Masking the image containing the nuclei with the boolean mask of the
        # fibers
        masked_image = ma.masked_array(labeled_image, mask)

        # Each gray level on the nuclei image corresponds to one nucleus
        nb_nuc = np.max(labeled_image)

        # For each nucleus, getting its center and calculating whether it is
        # inside or outside a fiber
        for i in range(1, nb_nuc + 1):

            nucleus_y, nucleus_x = np.where(labeled_image == i)
            center_x, center_y = np.mean(nucleus_x), np.mean(nucleus_y)

            in_fibre = ma.count_masked(masked_image[nucleus_y, nucleus_x])
            if in_fibre < fibre_threshold * nucleus_x.shape[0]:
                nuclei_out_fibre.append((center_x, center_y))
            else:
                nuclei_in_fibre.append((center_x, center_y))

        return nuclei_out_fibre, nuclei_in_fibre
