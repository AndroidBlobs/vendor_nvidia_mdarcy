#
# Copyright (c) 2018, NVIDIA Corporation.  All rights reserved.
#
# NVIDIA Corporation and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA Corporation is strictly prohibited.
#

import nvraw_v3
import array

class nvrawException(Exception):
    """ this exception is raised when errors occur during nvrawV3 read operations
    """
    def __init__ (self, errorCode, msg = ""):
        self.value = errorCode
        self.msg = msg

    def __str__(self):
        return "ERROR: %s\nErrorCode: %s: %s" % \
                (self.msg, repr(self.value), _nvcameratools.getErrorString(self.value))

# TODO: Add err debug messages to self.funclogger.error in next patch
class NvRawFileV3(object):
    def __init__(self):
        # ----------------------------
        # These (permanent) data members will be loaded the whole time
        self._loaded = False
        self._nvrfUniqueObj = None
        self._filename = None
        self._nvrfReader = None

        self._versionHeaderReader = None
        self._baseHeaderReader = None
        self._planeHeaderReader = None

        self._width = 0
        self._height = 0
        self._frameCount = 0
        self._planeCount = 0

        self._bitsPerSample = 0
        self._pixelFormat = 'int16'

        # TODO: fix self._exposurePlaneVector to be a vector per frame in next patch
        self._exposurePlaneVector = []

        # ----------------------------
        # These (temporary) data members will be loaded depending on which frame(s)
        # the user specifies
        self._exposurePlaneReader = []
        self._frameDataReader = []
        self._pixelDataReader = []
        self._pixelDataArray = []

        self._tempExposurePlaneReader = []
        self._tempFrameData = None
        self._tempFrameDataReader = []
        self._tempPixelData = None
        self._tempPixelDataReader = []
        self._tempPixelDataArray = []

        # Stores temporary data members in this list in the case the user specifies
        # more than 1 frame (range of frames)
        self._frameList = None
        #=============================

    def readFileV3(self, filename):
        err, nvrf3  = nvraw_v3.NvRawFileV3.openForReading(filename)
        if err:
            raise nvrawException(err, "Error while opening nvraw file for reading")
        self._nvrfUniqueObj = nvraw_v3.NvRawFileUniqueObj(nvrf3)
        self._loaded = True

        self._nvrfReader = nvraw_v3.INvRawFileReaderV1Cast(nvrf3)
        err, baseHeader = self._nvrfReader.getBaseHeader()
        if err:
            raise nvrawException(err, "Error while getting baseHeader chunk")

        self._baseHeaderReader = nvraw_v3.INvRawBaseHeaderReaderV1Cast(baseHeader)
        self._width = self._baseHeaderReader.getWidth()
        self._height = self._baseHeaderReader.getHeight()

        self._planeHeaderVector = nvraw_v3.NvRawPlaneHeaderVector()
        self._nvrfReader.getPlaneHeaders(self._planeHeaderVector)

        self._numPlanes = len(self._planeHeaderVector)
        for i in range(len(self._planeHeaderVector)):
            self._planeHeaderReader = nvraw_v3.INvRawPlaneHeaderReaderV1Cast(self._planeHeaderVector[i])

            self._bitsPerSample = self._planeHeaderReader.getBitsPerSample()
            self._pixelFormat = self._planeHeaderReader.getPixelFormat()
        return True

    def resetFramePointer(self):
        self.closeFile()
        err, nvrf3  = nvraw_v3.NvRawFileV3.openForReading(fileName)
        self._nvrfUniqueObj = nvraw_v3.NvRawFileUniqueObj(nvrf3)
        if err:
            raise nvrawException(err, "Error while opening nvraw file for reading")

        self._nvrfReader = nvraw_v3.INvRawFileReaderV1Cast(nvrf3)
        return True

    def jumpToFrame(self, frameNum):
        self._frameList = nvraw_v3.NvRawFrameVector()

        # traverses internal pointer to frameNumStart
        # with default parameters, this loop will do nothing. pinter will still be
        # at frame 0
        for i in range(frameNum):
            err = self._nvrfReader.getNextFrames(self._frameList, 1)
            if err:
                raise nvrawException(err, "Error while reading frames")

    def loadFrames(self, numFrames):
        # Load in the actual number of frames desired
        err = self._nvrfReader.getNextFrames(self._frameList, numFrames)
        if err:
            raise nvrawException(err, "Error while reading frames")

    def loadFrameReader(self, frameNum):
        frameReader = nvraw_v3.INvRawFrameReaderV1Cast(self._frameList[frameNum])
        self._exposurePlaneVector = nvraw_v3.NvRawExposurePlaneVector()
        err = frameReader.getExposurePlanes(self._exposurePlaneVector)
        if err:
            raise nvrawException(err, "Error while getting exposurePlanes")

    def loadExposurePlanes(self, planeNum):
        self._tempExposurePlaneReader.append(
            nvraw_v3.INvRawExposurePlaneReaderV1Cast(self._exposurePlaneVector[planeNum]))

    def loadFrameData(self, planeNum):
        err, self._tempFrameData = self._tempExposurePlaneReader[planeNum].getFrameData()
        if err:
            raise nvrawException(err, "Error while getting FrameData")

        self._tempFrameDataReader.append(
            nvraw_v3.INvRawFrameDataReaderV1Cast(self._tempFrameData))

    def loadPixelData(self, planeNum):
        err, self._tempPixelData = self._tempExposurePlaneReader[planeNum].getPixelData()
        if err:
            raise nvrawException(err, "Error while getting PixelData")

        self._tempPixelDataReader.append(
            nvraw_v3.INvRawPixelDataReaderV1Cast(self._tempPixelData))
        if (self._tempPixelDataReader[planeNum] == None):
            raise nvrawException(err, "Error with getting PixelData")

        pixelDataBlob = nvraw_v3.cdata(self._tempPixelDataReader[planeNum].getPixelData(),
                                        self._tempPixelDataReader[planeNum].getSize())
        self._tempPixelDataArray.append(array.array("h"))
        self._tempPixelDataArray[planeNum].fromstring(pixelDataBlob)

    def loadNvraw(self, frameNumStart = 0, numFrames = 1):
        del self._exposurePlaneReader[:]
        del self._frameDataReader[:]
        del self._pixelDataReader[:]
        del self._pixelDataArray[:]

        self.jumpToFrame(frameNumStart)
        self.loadFrames(numFrames)

        for i in range(len(self._frameList)):
            self.loadFrameReader(i)

            del self._tempExposurePlaneReader[:]
            self._tempFrameData = None
            del self._tempFrameDataReader[:]
            self._tempPixelData = None
            del self._tempPixelDataReader[:]
            del self._tempPixelDataArray[:]

            for j in range(len(self._exposurePlaneVector)):
                self.loadExposurePlanes(j)
                self.loadFrameData(j)
                self.loadPixelData(j)

            self._exposurePlaneReader.append(self._tempExposurePlaneReader)
            self._frameDataReader.append(self._tempFrameDataReader)
            self._pixelDataReader.append(self._tempPixelDataReader)
            self._pixelDataArray.append(self._tempPixelDataArray)

        self.closeFile()
        return True

    def closeFile():
        self._nvrfUniqueObj.get().close()


