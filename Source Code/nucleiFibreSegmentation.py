# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 12:05:16 2021

@author: Ibrahim
"""
# --------------------------------------------------------------------------
# libraries


from deepcell.applications import Mesmer  # het model te gebruiken
import numpy as np
import time
import cv2

# --------------------------------------------------------------------------
# functions
app = None


# initialise the mesmer app (happens while loading)
def initialize_mesmer():
    global app
    app = Mesmer()


def str_to_number_color(color_1, color_2):
    """
    Convert "r","g","b" into integers    

    Parameters
    ----------
    color_1 : str
        the color for the cells which could be "b" for blue, "r" for red and
        "g" for green.
    color_2 : str
        the color for the cytoplasm.(mulitplex tissue)

    Returns
    -------
    ret : List
        returns two integers in a list.

    """   

    if isinstance(color_1, str) and isinstance(color_2, str):
        colordict = {("Blue", "Green"): [0, 1],
                     ("Blue", "Red"): [0, 2],
                     ("Green", "Blue"): [1, 0],
                     ("Green", "Red"): [1, 2],
                     ("Red", "Green"): [2, 1],
                     ("Red", "Blue"): [2, 0]}
    else:
        raise ValueError("input needs to be of type str, got" +
                         type(color_1) + "and" + type(color_2))
    return colordict.get((color_1, color_2), [2, 1])  # default returns [2, 1]


def cellen_herkennen(image, whole_color, parameters):
    """
    Returns an image with labels of the nuclei that it counted.
    Each nucleus has its own unique number.
    If the nuclei on the image constitute of 200 pixels, then each of those
    200 pixels has the same number.

    Parameters
    ----------
    image : nd.array
        of shape (N,x,y,3) where N is amount of images. xy the height and width
        and 3 the rgb values of each pixel. (output readAllFiles)
    whole_color : List
        List of 2 integers (integers from 0 to 2). (output StrToNumberColor)
    parameters : List
        List of parameters for the prediction of the cells. 

    Returns
    -------
    labeledImageCollec : nd.array
        List of shape (N,x,y,1) where N is amount of images. 
        xy the height and width and each pixel has one certain value where 0 is
        background
        and other value are given to distinct nuclei.(mask)
    """
    
    # een klasse inladen
    # extract the desired colour from the image.
    # the predict function requires image with only 2 colors,
    # one for nuclei and other for cytoplasm(muliplex tissue)
    image_color = np.array([image[:, :, whole_color]])
        
    labeled_image = app.predict(image_color, batch_size=parameters[7],
                                image_mpp=parameters[8],
                                compartment='nuclear',
                                postprocess_kwargs_nuclear={
        'maxima_threshold': parameters[0],
        'maxima_smooth': parameters[1],
        'interior_threshold': parameters[2],
        'interior_smooth': parameters[3],
        'small_objects_threshold': parameters[4],
        'fill_holes_threshold': parameters[5],
        'radius': parameters[6]})

    return np.reshape(labeled_image[0],
                      (labeled_image.shape[1],
                       labeled_image.shape[2])).astype(np.uint16)


def fiber_detection_threshold_and_erode(green_channel, deepcell,
                                        do_fibre_counting):

    # apply first base threshold
    kernel = np.ones((5, 5), np.uint8)
    eerste_threshold = cv2.threshold(green_channel, 20, 255,
                                     cv2.THRESH_BINARY)[1]

    toegepast = cv2.bitwise_and(eerste_threshold, green_channel)
    gemiddelde_intensiteit_groen = cv2.mean(toegepast, eerste_threshold)[0]
    threshold = int(np.floor(0.7 * np.mean([gemiddelde_intensiteit_groen,
                                            cv2.mean(green_channel)[0]])))
    green_fibers_manual = cv2.threshold(green_channel, threshold, 255,
                                        cv2.THRESH_BINARY)[1]

    # apply an adaptive threshold
    test3 = cv2.countNonZero(green_fibers_manual)
    r3 = test3/(green_channel.shape[0] * green_channel.shape[1])

    threshold = int(np.floor((1.58 * r3) *
                             np.mean([gemiddelde_intensiteit_groen,
                                      cv2.mean(green_channel)[0]])))
    minimumthreshold = 20
    maximumthreshold = 36
    if threshold < minimumthreshold:
        threshold = minimumthreshold
    if threshold > maximumthreshold:
        threshold = maximumthreshold
    green_fibers_manual = cv2.threshold(green_channel, threshold, 255,
                                        cv2.THRESH_BINARY)[1]
    open_ = green_fibers_manual

    erode_op = cv2.morphologyEx(open_, cv2.MORPH_OPEN, kernel)

    # find contours of the fibers and remove smallest ones
    cnts = cv2.findContours(erode_op, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:

        if cv2.minEnclosingCircle(c)[1] < 100:  # 100
            cv2.drawContours(erode_op, [c], -1, (0, 0, 0), -1)

        elif cv2.arcLength(c, True) < 200:  # 200 if the perimeter of a fiber
            # is too short, it is excluded
            cv2.drawContours(erode_op, [c], -1, (0, 0, 0), -1)

        elif cv2.contourArea(c) < 1600:  # 2000 if the area of a fiber is
            # too small, it is excluded
            cv2.drawContours(erode_op, [c], -1, (0, 0, 0), -1)

    erode_op = cv2.morphologyEx(erode_op, cv2.MORPH_CLOSE, kernel)

    # remove holes in the fibres
    new = cv2.bitwise_not(erode_op)

    cnts = cv2.findContours(new, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        area = cv2.contourArea(c)

        if area < 1600:  # if the area of a hole is small enough,
            # it is filled in
            cv2.drawContours(new, [c], -1, (0, 0, 0), -1)

    new = cv2.bitwise_not(new)

    # convert to combines with the deepcell labeled image
    new16 = new.astype(np.uint16)
    new16[new16 >= 255] = 0b1111111111111111
    applied_deepcell = np.bitwise_and(deepcell, new16)

    # find contours of the fibers
    fibre_centres = []
    if do_fibre_counting:
        new = cv2.resize(new, None, fx=1/2, fy=1/2)  # for speed
        contours = cv2.findContours(new, cv2.RETR_CCOMP,
                                    cv2.CHAIN_APPROX_SIMPLE)
        cnts = contours[0] if len(contours) == 2 else contours[1]
        hierarchy = contours[1]
        for i, c in enumerate(cnts):

            # check if it is not a hole
            if hierarchy[0][i][3] == -1:

                # get geometrical centre
                m = cv2.moments(c)
                cx = int(m['m10'] / m['m00'])
                cy = int(m['m01'] / m['m00'])

                # cut out the contour
                black_im = np.zeros((new.shape[0] + 1, new.shape[1] + 1, 1),
                                    np.uint8)
                cv2.drawContours(black_im, [c], -1, 255, -1)

                # find all the holes
                for j in range(len(hierarchy[0])):
                    # if we are the parent (only one layer down will be
                    # scanned)
                    if hierarchy[0][j][3] == i:
                        cv2.drawContours(black_im, [cnts[j]], -1, 0, -1)

                # make first lines black (so that distance transform takes
                # border into account)
                black_im[0, :] = np.zeros((new.shape[1] + 1))[0]
                black_im[:, 0] = np.zeros((new.shape[0] + 1))[0]

                # do the distance transform
                dist_transform = cv2.distanceTransform(black_im,
                                                       cv2.DIST_L2, 3)
                max_dis = np.max(dist_transform)
                cv2.normalize(dist_transform, dist_transform, 0, 255,
                              cv2.NORM_MINMAX)
                percentile = np.percentile(dist_transform[dist_transform >
                                                          0.01], 80)

                # get centre
                above_percentile = np.where(dist_transform >= percentile)
                function = (cx - above_percentile[1]) ** 2 + \
                    (cy - above_percentile[0]) ** 2 - \
                    (dist_transform[above_percentile[0],
                                    above_percentile[1]] * max_dis / 255) ** 3
                min_index = np.argmin(function)
                fibre_centres.append([above_percentile[1][min_index] * 2,
                                      above_percentile[0][min_index] * 2])

    return applied_deepcell, fibre_centres


def fibre_detection__nuclei_positions(original,
                                      labeled_image,
                                      do_fibre_positions,
                                      fibre_threshold=0.85):

    list_tuple_location = []
    list_tuple_location_fibre = []

    # get the fibre detection
    applied, list_tuple_fibre_centres = fiber_detection_threshold_and_erode(
        original, labeled_image, do_fibre_positions)

    i = 1
    y_half_scan_range = 25
    prev_y = y_half_scan_range
    while True:  # each nuclei's distinct number from 1 to ...(maximum
        # amount of nuclei) where are the pixels in image k where
        # pixelvalue(distinct number) are i.

        # get lowest and highest ypixel scan
        lowest_y = max(0, prev_y - y_half_scan_range)
        highest_y = min(labeled_image.shape[0], prev_y + y_half_scan_range + 1)

        max_y = 0
        min_y = 0
        done = False

        while True:
            # scan for the nucleus inside this band
            alle_pixels = np.where(labeled_image[lowest_y:highest_y, :] == i)

            x_cos = alle_pixels[1]
            y_cos = alle_pixels[0]

            # check if we lost the nucleus
            if x_cos.shape[0] == 0:
                if lowest_y == 0 and highest_y == labeled_image.shape[0]:
                    done = True
                    break
                lowest_y = 0
                highest_y = labeled_image.shape[0]
                continue

            # get min and max
            min_y = np.min(y_cos) + lowest_y
            max_y = np.max(y_cos) + lowest_y

            # break if we found it fully
            if (min_y != lowest_y or min_y == 0) and \
                    (max_y != highest_y - 1 or max_y ==
                     labeled_image.shape[0] - 1):
                break

            # if we did not completely detect the nucleus
            if min_y == lowest_y:
                lowest_y -= 2 * y_half_scan_range
            elif max_y == highest_y-1:
                highest_y += 2 * y_half_scan_range

        if done:
            break

        # get bounding box (evt. gewoon vaste grootte nemen)
        min_x = np.min(x_cos)
        max_x = np.max(x_cos)

        # determine whether or not in fibre
        an = int(np.mean(y_cos)) + lowest_y  # ygem
        bn = int(np.mean(x_cos))  # xgem
        loc = [bn, an]
        prev_y = an

        # get number of pixels in total
        number_of_pixels = x_cos.shape[0]

        # get number of pixels in fibre
        number_of_fibre_pixels = np.count_nonzero(applied[min_y:max_y + 1,
                                                  min_x:max_x + 1] == i)

        # append to correct list
        if number_of_fibre_pixels / number_of_pixels >= fibre_threshold:
            list_tuple_location_fibre.append(loc)
        else:
            list_tuple_location.append(loc)
        i += 1

    return list_tuple_location, list_tuple_location_fibre, \
        list_tuple_fibre_centres


def deepcell_functie(filename,
                     kleurcellen,
                     kleurcyto,
                     do_fibre_counting,
                     small_objects_thresh):
    """
    :param filename: the name of the file to extract
    (filename.tif/filename.tiff -> without extension)
    :param kleurcellen:
    :param kleurcyto:
    :param do_fibre_counting:
    :param small_objects_thresh:
    :return: Two lists, one with centers of pixels outside of fibre, one with
    centers of pixels inside
    """

    t1 = time.time()

    # load the image
    image = cv2.imread(filename)

    t2 = time.time()

    amount_of_files = 8
    whole_color = str_to_number_color(kleurcellen, kleurcyto)
    print(whole_color)
    
    # deepclel post process parameters
    parameters = [0.05, 0, 0.3, 2, small_objects_thresh, 15, 2,
                  amount_of_files, None]  # veel sneller als mpp = None
    # parameters = [0.1, 0, 0.3, 2, 414, 15, 2, amount_of_files, None]

    # get the deepcell prediction segmentation mask
    labeled_image = cellen_herkennen(image, whole_color, parameters)

    t3 = time.time()
    # get the lists of fibre and nuclei centres
    list_tuple_location, list_tuple_location_fibre, \
        list_tuple_fibre_centres = fibre_detection__nuclei_positions(
            image[:, :, whole_color[1]], labeled_image, do_fibre_counting)

    t10 = time.time()
    print(t2 - t1, t3 - t2, (t10 - t3), t10 - t1)

    return list_tuple_location, list_tuple_location_fibre, \
        list_tuple_fibre_centres, image.shape[1], image.shape[0]


"""

#path aanpassen en zorgen dat foto met deze filename in die path te vinden is
l, b = deepcell_functie('ditiseenfoto')


print(l[:10])
print(b[:10])
"""

# define colours kan wel wat beter lol wtf
# doe sommige dingen maar één keer (lik define colours enal), soms kort maar
# lengt uit met veel foto's
