# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 12:05:16 2021

@author: Ibrahim
"""
#--------------------------------------------------------------------------
#libraries


from deepcell.applications import Mesmer # het model te gebruiken
import numpy as np
import random as rd
import time
import os
import cv2

#--------------------------------------------------------------------------
# functions
app = None

# initialise the mesmer app (happens while loading)
def initializeMesmer() :
    global app
    app = Mesmer()


def StrToNumberColor(color_1, color_2):
    """
    Convert "r","g","b" into integers    

    Parameters
    ----------
    color_1 : str
        the color for the cells which could be "b" for blue, "r" for red and "g" for green.
    color_2 : str
        the color for the cytoplasm.(mulitplex tissue)

    Returns
    -------
    ret : List
        returns two integers in a list.

    """   

    if isinstance(color_1, str) and isinstance(color_2, str):
        Colordict = {
            ("Blue", "Green") : [0,1],
            ("Blue", "Red") : [0,2],
            ("Green", "Blue") : [1,0],
            ("Green", "Red") : [1,2],
            ("Red", "Green") : [2,1],
            ("Red", "Blue") : [2,0]
        }
    else:
        raise ValueError("input needs to be of type str, got" + type(color_1) + "and" + type(color_2) )
    return Colordict.get((color_1, color_2), [2,1]) #default returns [2,1]

def cellenHerkennen(image, wholeColor,parameters):
    """
    Returns an image with labels of the nuclei that it counted.
    Each nuclei has its own unique number.
    If the nuclei on the image constitute of 200 pixels, then each of those 200 pixels has the same number.

    Parameters
    ----------
    imCollection : nd.array
        of shape (N,x,y,3) where N is amount of images. xy the heigt and width and 3 the rgb values of each pixel. (output readAllFiles)
    wholeColor : List
        List of 2 integers (integers from 0 to 2). (output StrToNumberColor)
    parameters : List
        List of parameters for the prediction of the cells. 

    Returns
    -------
    labeledImageCollec : nd.array
        List of shape (N,x,y,1) where N is amount of images. 
        xy the heigt and width and each pixel has one certain value where 0 is background 
        and other value are given to distinct nuclei.(mask)
    """
    
    # een klasse inladen
    #extract the desired colour from the image. 
    #the predict function requires image with only 2 colors, 
    #one for nuclei and other for cytoplasm(muliplex tissue)
    imageColor = np.array([image[:,:,wholeColor]])
        
    labeledImage = app.predict(imageColor,batch_size=parameters[7],
                                     image_mpp=parameters[8],
                                     compartment='nuclear',
                                     postprocess_kwargs_nuclear={
                                                     'maxima_threshold': parameters[0],
                                                     'maxima_smooth': parameters[1],
                                                     'interior_threshold': parameters[2],
                                                     'interior_smooth': parameters[3],
                                                     'small_objects_threshold': parameters[4],
                                                     'fill_holes_threshold': parameters[5],
                                                     'radius': parameters[6] })        

    return np.reshape(labeledImage[0], (labeledImage.shape[1], labeledImage.shape[2])).astype(np.uint16)

def FiberDetectionThresholdandErode(greenChannel, deepcell, doFibreCounting):

    # apply first base threshold
    kernel = np.ones((5, 5), np.uint8)
    eersteThreshold = cv2.threshold(greenChannel, 20, 255, cv2.THRESH_BINARY)[1]

    toegepast = cv2.bitwise_and(eersteThreshold, greenChannel)
    gemiddeldeIntensiteitGroen = cv2.mean(toegepast, eersteThreshold)[0]
    threshold = int(np.floor(0.7 * np.mean([gemiddeldeIntensiteitGroen, cv2.mean(greenChannel)[
        0]])))
    GreenFibersManual = cv2.threshold(greenChannel, threshold, 255, cv2.THRESH_BINARY)[1]

    # apply an adaptive threshold
    test3 = cv2.countNonZero(GreenFibersManual)
    r3 = test3/(greenChannel.shape[0]*greenChannel.shape[1])


    threshold = int(np.floor((1.58 * r3) * np.mean([gemiddeldeIntensiteitGroen, cv2.mean(greenChannel)[
        0]])))
    minimumthreshold = 20
    maximumthreshold = 36
    if threshold < minimumthreshold:
        threshold = minimumthreshold
    if threshold > maximumthreshold:
        threshold = maximumthreshold
    GreenFibersManual = cv2.threshold(greenChannel, threshold, 255, cv2.THRESH_BINARY)[1]
    open = GreenFibersManual

    erode_op = cv2.morphologyEx(open, cv2.MORPH_OPEN, kernel)

    # find contours of the fibers and remove smallest ones
    cnts = cv2.findContours(erode_op, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:

        if cv2.minEnclosingCircle(c)[1] < 100:  # 100
            cv2.drawContours(erode_op, [c], -1, (0, 0, 0), -1)

        elif cv2.arcLength(c, True) < 200:  # 200 if the perimeter of a fiber is too short, it is excluded
            cv2.drawContours(erode_op, [c], -1, (0, 0, 0), -1)

        elif cv2.contourArea(c) < 1600:  # 2000 if the area of a fiber is too small, it is excluded
            cv2.drawContours(erode_op, [c], -1, (0, 0, 0), -1)

    erode_op = cv2.morphologyEx(erode_op, cv2.MORPH_CLOSE, kernel)

    # remove holes in the fibres
    new = cv2.bitwise_not(erode_op)

    cnts = cv2.findContours(new, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        area = cv2.contourArea(c)

        if area < 1600:  # if the area of a hole is small enough, it is filled in
            cv2.drawContours(new, [c], -1, (0, 0, 0), -1)

    new = cv2.bitwise_not(new)

    # convert to combines with the deepcell labeled image
    new16 = new.astype(np.uint16)
    new16[new16 >= 255] = 0b1111111111111111
    applied_deepcell = np.bitwise_and(deepcell, new16)


    # find contours of the fibers
    fibreCentres = []
    if doFibreCounting : 
        new = cv2.resize(new, None, fx=1/2, fy=1/2) # for speed
        contours = cv2.findContours(new, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        cnts = contours[0] if len(contours) == 2 else contours[1]
        hierarchy = contours[1]
        for i,c in enumerate(cnts) :

            # check if it is not a hole
            if hierarchy[0][i][3] == -1:

                # get geometrical centre
                M = cv2.moments(c)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])

                # cut out the contour
                blackIm = np.zeros((new.shape[0]+1, new.shape[1]+1, 1), np.uint8)
                cv2.drawContours(blackIm, [c], -1, (255), -1)

                # find all the holes
                for j in range(len(hierarchy[0])) :
                    # if we are the parent (only one layer down will be scanned)
                    if hierarchy[0][j][3] == i :
                        cv2.drawContours(blackIm, [cnts[j]], -1, (0), -1)


                # make first lines black (so that distance transform takes border into account)
                blackIm[0,:] = np.zeros((new.shape[1]+1))[0]
                blackIm[:,0] = np.zeros((new.shape[0]+1))[0]

                # do the distance transform
                distTransform = cv2.distanceTransform(blackIm, cv2.DIST_L2, 3)
                maxDis = np.max(distTransform)
                cv2.normalize(distTransform, distTransform, 0, 255, cv2.NORM_MINMAX)
                percentile = np.percentile(distTransform[distTransform > 0.01],80)

                # get centre
                abovePercentile = np.where(distTransform >= percentile)
                function = (cx - abovePercentile[1])**2 + (cy - abovePercentile[0])**2 - (distTransform[abovePercentile[0], abovePercentile[1]]*maxDis/255)**3
                minIndex = np.argmin(function)
                fibreCentres.append([abovePercentile[1][minIndex]*2,abovePercentile[0][minIndex]*2])

    return applied_deepcell, fibreCentres

def FibreDetection_NucleiPositions(original, labeledImage, doFibrePositions, fibreThreshold = 0.85) :

    ListTupleLocation = []
    ListTupleLocationFibre = []

    # get the fibre detection
    applied, listTupleFibreCentres = FiberDetectionThresholdandErode(original, labeledImage, doFibrePositions)

    i = 1
    yHalfScanRange = 25
    prevY = yHalfScanRange
    while(True): # each nuclei's dinstinct number from 1 to ...(maximum amount of nuclei)
        # where are the pixels in image k where pixelvlaue(disntict number) are i.

        # get lowest and highest ypixel scan
        lowestY = max(0,prevY - yHalfScanRange)
        highestY = min(labeledImage.shape[0],prevY + yHalfScanRange + 1)

        allePixels = None
        maxY = 0
        minY = 0
        XCos = None
        YCos = None
        done = False


        while (True) :
            # scan for the nucleus inside this band
            allePixels = np.where(labeledImage[lowestY:highestY,:] == i)

            XCos = allePixels[1]
            YCos = allePixels[0]

            # check if we lost the nucleus
            if XCos.shape[0] == 0:
                if (lowestY == 0 and highestY == labeledImage.shape[0]) :
                    done = True
                    break
                lowestY = 0
                highestY = labeledImage.shape[0]
                continue

            # get min and max
            minY = np.min(YCos) + lowestY
            maxY = np.max(YCos) + lowestY

            # break if we found it fully
            if (minY != lowestY or minY == 0) and (maxY != highestY-1 or maxY == labeledImage.shape[0] - 1):
                break

            # if we did not completely detect the nucleus
            if minY == lowestY :
                lowestY -= 2 * yHalfScanRange
            elif maxY == highestY-1 :
                highestY += 2 * yHalfScanRange

        if (done) :
            break

        # get bounding box (evt. gewoon vaste grootte nemen)
        minX = np.min(XCos)
        maxX = np.max(XCos)

        # determine whether or not in fibre
        an = int(np.mean(YCos)) + lowestY #ygem
        bn = int(np.mean(XCos)) #xgem
        loc = [bn,an]
        prevY = an

        # get number of pixels in total
        numberOfPixels = XCos.shape[0]

        # get number of pixels in fibre
        numberOfFibrePixels = np.count_nonzero(applied[minY:maxY+1, minX:maxX+1] == i)

        # append to correct list
        if numberOfFibrePixels / numberOfPixels >= fibreThreshold :
            ListTupleLocationFibre.append(loc)
        else :
            ListTupleLocation.append(loc)
        i += 1

    return ListTupleLocation, ListTupleLocationFibre, listTupleFibreCentres


def deepcell_functie(filename, kleurcellen, kleurcyto, doFibreCounting, smallObjectsThresh ):
    '''
    :param path: the path from which to extract the .tif or .tiff image
    :param filename: the name of the file to extract (filename.tif/filename.tiff -> without extension)
    :return: Two lists, one with centers of pixels outside of fibre, one with centers of pixels
    inside
    '''


    t1 = time.time()

    # load the image
    image = cv2.imread(filename)

    t2 = time.time()

    amountOfFiles = 8
    wholeColor = StrToNumberColor(kleurcellen, kleurcyto)
    print(wholeColor)
    
    # deepclel post process parameters
    parameters= [0.05, 0, 0.3, 2, smallObjectsThresh , 15, 2, amountOfFiles, None] #veel sneller als mpp = None
    #parameters= [0.1, 0, 0.3, 2, 414 , 15, 2, amountOfFiles, None]

    # get the deepcell prediction segmentation mask
    labeledImage = cellenHerkennen(image, wholeColor, parameters)

    t3 = time.time()
    # get the lists of fibre and nuclei centres
    ListTupleLocation, ListTupleLocationFibre, listTupleFibreCentres = FibreDetection_NucleiPositions(image[:,:,wholeColor[1]], labeledImage, doFibreCounting)

    t10 = time.time()
    print(t2-t1,t3-t2,(t10-t3), t10-t1)

    return ListTupleLocation, ListTupleLocationFibre, listTupleFibreCentres, image.shape[1], image.shape[0]

'''

#path aanpassen en zorgen dat foto met deze filename in die path te vinden is
l, b = deepcell_functie('ditiseenfoto')


print(l[:10])
print(b[:10])
'''

# define colours kan wel wat beter lol wtf
# doe sommige dingen maar één keer (lik define colours enal), soms kort maar lengt uit met veel foto's