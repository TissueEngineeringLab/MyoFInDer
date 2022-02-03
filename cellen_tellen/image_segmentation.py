# coding: utf-8

from deepcell.applications import Mesmer
import numpy as np
import numpy.ma as ma
from pathlib import Path
import cv2

numpy_color_to_int = {"Blue": 0,
                      "Green": 1,
                      "Red": 2}


class Image_segmentation:

    def __init__(self):
        self._app = Mesmer()

    def __call__(self,
                 path: Path,
                 nuclei_color: str,
                 fibre_color: str,
                 count_fibres: bool,
                 small_objects_threshold: int):

        colors = [numpy_color_to_int[nuclei_color],
                  numpy_color_to_int[fibre_color]]

        image = cv2.imread(str(path))

        two_channel_image = np.array([image[:, :, colors]])

        maxima_threshold = 0.05
        maxima_smooth = 0
        interior_threshold = 0.3
        interior_smooth = 2
        fill_holes_threshold = 15
        radius = 2
        microns_per_pixel = None
        batch_size = 8

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

        labeled_image = np.squeeze(labeled_image)

        mask, mask_8bit = self._get_fibre_mask(image[:, :, colors[1]])
        if count_fibres:
            fibre_centers = self._fibre_detection(mask_8bit)
        else:
            fibre_centers = []

        nuclei_out, nuclei_in = self._get_nuclei_positions(labeled_image, mask)

        return nuclei_out, nuclei_in, fibre_centers

    @staticmethod
    def _get_fibre_mask(fibre_channel):
        # apply first base threshold
        kernel = np.ones((5, 5), np.uint8)
        _, binary_thresh = cv2.threshold(fibre_channel, 25, 255,
                                         cv2.THRESH_BINARY)

        # Opening, to remove noise in the background
        processed = cv2.morphologyEx(binary_thresh,
                                     cv2.MORPH_OPEN, kernel)

        # Find contours of the fibers
        contours, _ = cv2.findContours(processed, cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)
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

        # Fills the fibres in white on the labeled image
        mask = processed.astype(bool)

        return mask, processed

    @staticmethod
    def _fibre_detection(mask_8bit):

        # find contours of the fibers
        fibre_centres = []
        # Resize the image to speed up
        processed = cv2.resize(mask_8bit, None, fx=0.5, fy=0.5)
        # Find contours
        contours, hierarchy = cv2.findContours(processed, cv2.RETR_CCOMP,
                                               cv2.CHAIN_APPROX_SIMPLE)
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
                    [(top_20_percent[1][min_index] - 1) * 2,
                     (top_20_percent[0][min_index] - 1) * 2])

        return fibre_centres

    @staticmethod
    def _get_nuclei_positions(labeled_image,
                              mask,
                              fibre_threshold=0.85):

        nuclei_out_fibre = []
        nuclei_in_fibre = []

        masked_image = ma.masked_array(labeled_image, mask)

        nb_nuc = np.max(labeled_image)

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
