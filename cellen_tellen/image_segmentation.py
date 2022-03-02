# coding: utf-8

from deepcell.applications import Mesmer
import numpy as np
import numpy.ma as ma
from pathlib import Path
import cv2
from typing import List, Tuple

# Table for converting color strings to channels, assuming BGR images
numpy_color_to_int = {"blue": 0,
                      "green": 1,
                      "red": 2}


class Image_segmentation:
    """Class for processing images, detecting fibers and nuclei."""

    def __init__(self) -> None:
        """Simply loads the Mesmer library."""

        self._app = Mesmer()

    def __call__(self,
                 path: Path,
                 nuclei_color: str,
                 fibre_color: str,
                 count_fibres: bool,
                 small_objects_threshold: int) -> \
            Tuple[List[Tuple[np.ndarray, np.ndarray]],
                  List[Tuple[np.ndarray, np.ndarray]],
                  List[Tuple[int, int]]]:
        """Computes the nuclei positions and optionally the fibers positions.

        Also returns whether the nuclei are inside or outside the fibers.

        Args:
            path: The path to the image to process.
            nuclei_color: The color of the nuclei, as a string.
            fibre_color: The color of the fibres, as a string.
            count_fibres: if True, detects and counts the fibres.
            small_objects_threshold: Objects whose area is lower than this
                value (in pixels) will not be considered.

        Returns:
            The list of nuclei outside the fibres, the list of nuclei inside
            the fibers, and the list of fibre centers.
        """

        # Converting colors from string to int
        colors = [numpy_color_to_int[nuclei_color],
                  numpy_color_to_int[fibre_color]]

        # Loads the image and keeps only the nuclei and fibres channels
        image = cv2.imread(str(path))
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
        mask, mask_8bit = self._get_fibre_mask(image[:, :, colors[1]])

        # Getting the center of the fibers
        fibre_centers = self._fibre_detection(mask_8bit) if count_fibres \
            else []

        # Getting the position of the nuclei
        nuclei_out, nuclei_in = self._get_nuclei_positions(labeled_image, mask)

        return nuclei_out, nuclei_in, fibre_centers

    @staticmethod
    def _get_fibre_mask(fibre_channel: np.ndarray) -> Tuple[np.ndarray,
                                                            np.ndarray]:
        """Applies several images processing methods to the fibre channel of
        the image to smoothen the outline.

        Args:
            fibre_channel: The channel of the image containing the fibres.

        Returns:
            A boolean mask containing the position of the fibres, and an 8-bits
            image of the fibers.
        """

        # First, apply a base threshold
        kernel = np.ones((5, 5), np.uint8)
        _, binary_thresh = cv2.threshold(fibre_channel, 25, 255,
                                         cv2.THRESH_BINARY)

        # Opening, to remove noise in the background
        processed = cv2.morphologyEx(binary_thresh,
                                     cv2.MORPH_OPEN, kernel)

        # Find contours of the fibers
        contours, _ = cv2.findContours(processed, cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)

        # Correcting the obtained contours
        for contour in contours:
            # Fill if enclosing circle smaller than 100 pixels
            if cv2.minEnclosingCircle(contour)[1] < 100:  # 100
                cv2.drawContours(processed, [contour], -1, (0, 0, 0), -1)

            # Fill if perimeter smaller than 200 pixels
            elif cv2.arcLength(contour, True) < 200:
                cv2.drawContours(processed, [contour], -1, (0, 0, 0), -1)

            # Fill if enclosed area smaller than 1600 pixels
            elif cv2.contourArea(contour) < 1600:
                cv2.drawContours(processed, [contour], -1, (0, 0, 0), -1)

        # Closing, to remove noise inside the fibres
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)

        # Inverting black and white
        processed = cv2.bitwise_not(processed)

        # Find contours of the holes inside the fibers
        contours, _ = cv2.findContours(processed, cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Fill hole if its area is smaller than 1600 pixels
            if cv2.contourArea(contour) < 1600:
                cv2.drawContours(processed, [contour], -1, (0, 0, 0), -1)

        # Inverting black and white again
        processed = cv2.bitwise_not(processed)

        # Creating a boolean mask, later used to generate a masked array
        mask = processed.astype(bool)

        return mask, processed

    @staticmethod
    def _fibre_detection(mask_8bit: np.ndarray) -> List[Tuple[int, int]]:
        """Applies several filters to the fiber channel of the image, and
        determines a "center" for the detected fibers.

        Args:
            mask_8bit: The fiber channel of the image.

        Returns:
            A list containing the centers of the fibers.
        """

        fibre_centres = []
        # Resizing the image to speed up the processing
        processed = cv2.resize(mask_8bit, None, fx=0.5, fy=0.5)

        # Finding the contours
        contours, hierarchy = cv2.findContours(processed, cv2.RETR_CCOMP,
                                               cv2.CHAIN_APPROX_SIMPLE)

        # Iterating on the contours
        if hierarchy is not None:
            for i, (contour, level) in enumerate(zip(contours, hierarchy[0])):
                # Objects that have a parent are just holes
                if level[3] == -1:

                    # Calculates the centroid of the contour
                    m = cv2.moments(contour)
                    cx = int(m['m10'] / m['m00'])
                    cy = int(m['m01'] / m['m00'])

                    # Fill contours white on a black background
                    black_im = np.zeros(processed.shape, np.uint8)
                    cv2.drawContours(black_im, [contour], -1, 255, -1)

                    # Fill all the holes black
                    holes = [con for con, lvl in zip(contours, hierarchy[0])
                             if lvl[3] == i]
                    if holes:
                        cv2.drawContours(black_im, holes, -1, 0, -1)

                    # Make a black contour to count border in the distance
                    # transform
                    black_im = np.vstack(
                        [np.zeros(black_im.shape[1]).astype(np.uint8),
                         black_im])
                    black_im = np.vstack(
                        [black_im,
                         np.zeros(black_im.shape[1]).astype(np.uint8)])
                    black_im = np.hstack(
                        [np.zeros((black_im.shape[0], 1)).astype(np.uint8),
                         black_im])
                    black_im = np.hstack(
                        [black_im,
                         np.zeros((black_im.shape[0], 1)).astype(np.uint8)])

                    # Apply a distance transform
                    dist_transform = cv2.distanceTransform(black_im,
                                                           cv2.DIST_L2, 3)
                    max_dist = np.max(dist_transform)

                    # Cast the distance to an 8 bit image
                    cv2.normalize(dist_transform, dist_transform, 0, 255,
                                  cv2.NORM_MINMAX)

                    # All values above this one are in the top 20%
                    percent_80 = np.percentile(dist_transform[dist_transform >
                                                              0.01], 80)

                    # Keep only the areas far from the fiber and image borders
                    top_20_percent = np.where(dist_transform >= percent_80)

                    # Compromise between being close to the centroid and far
                    # from the borders
                    norm = (cx - top_20_percent[1]) ** 2 + \
                           (cy - top_20_percent[0]) ** 2 - \
                           (dist_transform[top_20_percent[0],
                                           top_20_percent[1]] *
                            max_dist / 255) ** 3
                    min_index = np.argmin(norm)
                    fibre_centres.append(
                        ((top_20_percent[1][min_index] - 1) * 2,
                         (top_20_percent[0][min_index] - 1) * 2))

        return fibre_centres

    @staticmethod
    def _get_nuclei_positions(labeled_image: np.ndarray,
                              mask: np.ndarray,
                              fibre_threshold: float = 0.85) -> \
            Tuple[List[Tuple[np.ndarray, np.ndarray]],
                  List[Tuple[np.ndarray, np.ndarray]]]:
        """

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
            center_x = np.mean(nucleus_x)
            center_y = np.mean(nucleus_y)

            in_fibre = ma.count_masked(masked_image[nucleus_y, nucleus_x])
            if in_fibre < fibre_threshold * nucleus_x.shape[0]:
                nuclei_out_fibre.append((center_x, center_y))
            else:
                nuclei_in_fibre.append((center_x, center_y))

        return nuclei_out_fibre, nuclei_in_fibre
