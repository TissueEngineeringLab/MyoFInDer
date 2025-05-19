# coding: utf-8

import cellpose.models
import numpy as np
import numpy.ma as ma
from pathlib import Path
import cv2
from typing import List, Tuple, Any
from collections import defaultdict

from .tools import check_image

# Table for converting color strings to channels, assuming BGR images
numpy_color_to_int = {"red": 0,
                      "green": 1,
                      "blue": 2}


class ImageSegmentation:
    """Class for processing images, detecting fibers and nuclei."""

    def __init__(self) -> None:
        """Simply loads the Mesmer library."""

        self._app = cellpose.models.CellposeModel(diam_mean=17,
                                                  model_type='nuclei')

    def __call__(self,
                 path: Path,
                 nuclei_color: str,
                 fiber_color: str,
                 minimum_fiber_intensity: int,
                 maximum_fiber_intensity: int,
                 minimum_nucleus_intensity: int,
                 maximum_nucleus_intensity: int,
                 minimum_nucleus_diameter: int,
                 minimum_nuclei_count: int
                 ) -> Tuple[Path, List[Tuple[np.ndarray, np.ndarray]],
                            List[Tuple[np.ndarray, np.ndarray]],
                            Tuple[Any, ...], float]:
        """Computes the nuclei positions and optionally the fibers positions.

        Also returns whether the nuclei are inside or outside the fibers.

        Args:
            path: The path to the image to process.
            nuclei_color: The color of the nuclei, as a string.
            fiber_color: The color of the fibers, as a string.
            minimum_fiber_intensity: The gray level intensity above which a
                pixel is considered to be part of a fiber.
            maximum_fiber_intensity: The gray level intensity below which a
                pixel is considered to be part of a fiber.
            minimum_nucleus_intensity: Any nucleus whose average brightness is
                lower than this value will be discarded.
            maximum_nucleus_intensity: Any nucleus whose average brightness is
                greater than this value will be discarded.
            minimum_nucleus_diameter: Objects whose area is lower than this
                value (in pixels) will not be considered.
            minimum_nuclei_count: Nuclei located in a fiber containing less
                than this number of positive nuclei will be counted as
                negative.

        Returns:
            The list of nuclei outside the fibers, the list of nuclei inside
            the fibers, the list of fiber contours, and the ratio of fiber area
            over the total area.
        """

        # Converting colors from string to int
        colors = [numpy_color_to_int[nuclei_color],
                  numpy_color_to_int[fiber_color]]

        # Loads the image and keeps only the nuclei and fibers channels
        image = check_image(path)

        # The image couldn't be loaded
        if image is None:
            raise IOError("Could not load the image for segmentation, "
                          "aborting !")

        nuclei_channel = image[:, :, colors[0]]
        fiber_channel = image[:, :, colors[1]]

        del image

        small_objects_threshold = int(minimum_nucleus_diameter ** 2
                                      * np.pi / 4)

        # Actual nuclei detection function
        labeled_image, *_ = self._app.eval(
            x=np.stack((nuclei_channel,
                        np.zeros_like(nuclei_channel)),
                       axis=-1),
            batch_size=8,
            resample=None,
            channels=None,
            channel_axis=2,
            z_axis=None,
            normalize=True,
            invert=False,
            rescale=None,
            diameter=None,
            flow_threshold=0.4,
            cellprob_threshold=0.0,
            do_3D=False,
            anisotropy=None,
            flow3D_smooth=0,
            stitch_threshold=0.0,
            min_size=small_objects_threshold,
            max_size_fraction=1.0,
            niter=None,
            augment=False,
            tile_overlap=0.1,
            bsize=256,
            compute_masks=True,
            progress=None)

        # Getting the fiber mask
        mask = self._get_fiber_mask(fiber_channel,
                                    nuclei_channel,
                                    minimum_fiber_intensity,
                                    maximum_fiber_intensity)

        del fiber_channel

        # Calculating the area of fibers over the total area
        area = np.count_nonzero(mask) / mask.shape[0] / mask.shape[1]

        # Finding the contours of the fibers
        mask_8_bits = (mask * 255).astype('uint8')
        fiber_contours, _ = cv2.findContours(mask_8_bits, cv2.RETR_LIST,
                                             cv2.CHAIN_APPROX_SIMPLE)
        fiber_contours = tuple(map(np.squeeze, fiber_contours))

        # Getting the position of the nuclei
        nuclei_out, nuclei_in = self._get_nuclei_positions(
            labeled_image, mask, nuclei_channel, 0.75,
            minimum_nucleus_intensity, maximum_nucleus_intensity,
            minimum_nuclei_count)

        return path, nuclei_out, nuclei_in, fiber_contours, area

    @staticmethod
    def _get_fiber_mask(fiber_channel: np.ndarray,
                        nuclei_channel: np.ndarray,
                        minimum_intensity: int,
                        maximum_intensity: int) -> np.ndarray:
        """Applies several images processing methods to the fiber channel of
        the image to smoothen the outline.

        Args:
            fiber_channel: The channel of the image containing the fibers.
            nuclei_channel: The channel of the image containing the nuclei.
            minimum_intensity: The gray level intensity above which a pixel is
                considered to be part of a fiber.
            minimum_intensity: The gray level intensity below which a pixel is
                considered to be part of a fiber.

        Returns:
            A boolean mask containing the position of the fibers
        """

        # Apply a Gaussian filter to smoothen the fiber signal
        dim = int(min(fiber_channel.shape) / 50) // 2 * 2 - 1
        fiber_channel = cv2.GaussianBlur(fiber_channel, (dim, dim), 0)

        # First, apply a base threshold
        kernel = np.ones((4, 4), np.uint8)
        _, min_thresh = cv2.threshold(fiber_channel, minimum_intensity, 255,
                                      cv2.THRESH_BINARY)
        _, max_thresh = cv2.threshold(fiber_channel, maximum_intensity, 255,
                                      cv2.THRESH_BINARY)
        processed = min_thresh - max_thresh
        del min_thresh, max_thresh

        # Opening, to remove noise in the background
        processed = cv2.morphologyEx(processed,
                                     cv2.MORPH_OPEN, kernel)

        # Closing, to remove noise inside the fibers
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)

        # Find contours and hierarchy of the holes inside the fibers
        contours, hierarchy = cv2.findContours(processed, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        hierarchy = np.squeeze(hierarchy).tolist()

        # Define thresholds for filling up the inside holes
        thresh_nuc, _ = cv2.threshold(nuclei_channel, 0, 255, cv2.THRESH_OTSU)
        med_excl = np.median(nuclei_channel[processed > 0])

        for contour, (_, _, _, parent) in zip(contours, hierarchy):

            # Only consider inside contours
            if parent < 0:
                continue

            # Create a mask for the current contour
            mask = np.zeros_like(processed)
            cv2.drawContours(mask, (contour,), -1, 255, -1)

            # If the hole in the fiber signal is below a nucleus, and the fiber
            # signal is still quite bright, then fill up the hole
            if (np.average(nuclei_channel[mask.nonzero()]) > thresh_nuc and
                np.average(fiber_channel[mask.nonzero()]) > med_excl):
                cv2.drawContours(processed, (contour,), -1, 255, -1)

        # Creating a boolean mask, later used to generate a masked array
        mask = processed.astype(bool)

        return mask

    @staticmethod
    def _get_nuclei_positions(labeled_image: np.ndarray,
                              mask: np.ndarray,
                              nuclei_channel: np.ndarray,
                              fiber_overlap_threshold: float,
                              minimum_nucleus_intensity: int,
                              maximum_nucleus_intensity: int,
                              minimum_nuclei_count: int
                              ) -> Tuple[List[Tuple[np.ndarray, np.ndarray]],
                                         List[Tuple[np.ndarray, np.ndarray]]]:
        """Computes the center of the nuclei and determines whether they're
        positive or not.

        Args:
            labeled_image: The image containing the nuclei.
            mask: The boolean mask of the fibers.
            nuclei_channel: The channel of the image containing the nuclei.
            fiber_overlap_threshold: Fraction of area above which a nucleus is
                considered to be inside a fiber.
            minimum_nucleus_intensity: Any nucleus whose average brightness is
                lower than this value will be discarded.
            maximum_nucleus_intensity: Any nucleus whose average brightness is
                greater than this value will be discarded.
            minimum_nuclei_count: Nuclei located in a fiber containing less
                than this number of positive nuclei will be counted as
                negative.

        Returns:
            The list of the centers of nuclei outside of fibers, and the list
            of centers of nuclei inside fibers
        """

        nuclei_out_fiber = list()
        nuclei_in_fiber = list()

        # Detect the contours of the detected fibers
        contours, hierarchy = cv2.findContours(mask.astype(np.uint8),
                                               cv2.RETR_CCOMP,
                                               cv2.CHAIN_APPROX_SIMPLE)
        hierarchy = np.squeeze(hierarchy).tolist()

        # Group the contours so that the holes are with their parents
        grouped = defaultdict(list)
        for i, (contour, (_, _, _, parent)) in enumerate(zip(contours,
                                                             hierarchy)):
            if parent < 0:
                grouped[i].append(contour)
            else:
                grouped[parent].append(contour)

        # Dict to keep track of the nuclei count in each fiber
        nuc_count = {i: 0 for i in grouped.keys()}

        # Create fiber masks to check in which fiber each positive nucleus is
        fib_masks = dict()
        for i, cont in grouped.items():
            fib_mask = np.zeros_like(mask, dtype=np.uint8)
            cv2.drawContours(fib_mask, cont, -1, 255, -1)
            fib_mask = fib_mask.astype(bool)
            fib_mask = ma.masked_array(labeled_image, fib_mask)
            fib_masks[i] = fib_mask

        # Masking the image containing the nuclei with the boolean mask of the
        # fibers
        masked_image = ma.masked_array(labeled_image, mask)

        # Each gray level on the nuclei image corresponds to one nucleus
        nb_nuc = np.max(labeled_image)

        # Buffers for storing the nuclei, their positivity status, and the
        # index of the fiber in which they are located
        nuclei = dict()
        positivity = dict()
        fiber_num = dict()

        # Iterating through the detected nuclei
        for i in range(1, nb_nuc + 1):

            # Getting a list of the detected pixels
            nucleus_y, nucleus_x = np.where(labeled_image == i)
            center_x, center_y = np.mean(nucleus_x), np.mean(nucleus_y)

            # Aborting for the current nucleus if it's not bright enough
            if not (minimum_nucleus_intensity <=
                    np.average(nuclei_channel[nucleus_y, nucleus_x]) <=
                    maximum_nucleus_intensity):
                nuclei[i] = None
                positivity[i] = None
                fiber_num[i] = None
                continue

            # Determining whether the nucleus is positive or negative
            in_fiber = ma.count_masked(masked_image[nucleus_y, nucleus_x])
            if in_fiber < fiber_overlap_threshold * nucleus_x.shape[0]:
                positive = False
            else:
                positive = True

            # Storing the nucleus position and positivity
            nuclei[i] = (center_x, center_y)
            positivity[i] = positive

            # Searching for the first fiber that contains part of the nucleus
            if positive:
                for j, fib_mask in fib_masks.items():
                    if ma.count_masked(fib_mask[nucleus_y, nucleus_x]):
                        nuc_count[j] += 1
                        fiber_num[i] = j
                        break
            else:
                fiber_num[i] = None

        # Excluding the fibers that contain too few nuclei
        fib_to_ban = tuple(i for i, count in nuc_count.items()
                           if count < minimum_nuclei_count)

        # Iterating again over the detected nuclei
        for i in range(1, nb_nuc + 1):

            # Means that the nucleus was skipped due to out-of-bounds intensity
            if nuclei[i] is None:
                continue

            center_x, center_y = nuclei[i]
            positive = positivity[i]
            fib_num = fiber_num[i]

            # Excluding the nuclei belonging to fibers with too few nuclei
            if fib_num is not None and fib_num in fib_to_ban:
                positive = False

            # Building the final lists of positive and negative nuclei
            if positive:
                nuclei_in_fiber.append((center_x, center_y))
            else:
                nuclei_out_fiber.append((center_x, center_y))

        return nuclei_out_fiber, nuclei_in_fiber
