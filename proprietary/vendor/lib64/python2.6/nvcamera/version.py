# Copyright (c) 2010-2017, NVIDIA Corporation.  All rights reserved.
#
# NVIDIA Corporation and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA Corporation is strictly prohibited.
#

# this is nvcamera module version
__version__ = "5.0.4"

# Version history:
# "2.0.1" to "3.0.1" :  Change 681350 (nvcs: Changes for Automotive support)
# "3.0.1" to "3.0.2" :  Change 736886 (nvcs: nvcs: Add CamProperty PROP_HDR_RATIO_OVERRIDE)
# "3.0.2" to "4.0.0" :  Change 496301 (nvcs: Add streaming and per frame apis to nvcs)
# "4.0.0" to "4.0.1" :  Change 785680 (nvcs: sensor mode support to capture script)
# "4.0.1" to "4.1.0" :  Change 807634 (nvcs: add support for aperture properties)
# "4.1.0" to "4.1.1" :  Version is reserved.
# "4.1.1" to "4.1.2" :  Change 1127023 (nvcs: fix a logic to decide max resolution)
# "4.1.2" to "5.0.0" :  Change 1148656 (nvcs: add support for new APIs)
# "5.0.0" to "5.0.1" :  Change 1281032 (nvcs: Display more sensor info)
# "5.0.3"            :  Change 1305875 (nvcs: Add HDR support for nvcs)
# "5.0.3" to "5.0.4" :  Change 1297494 (conformance: set file permission on creation)


class NvCameraVersion:
    "Version Class"

    def getMajor(self):
        ver = __version__.split('.')
        assert len(ver) >= 3
        return int(ver[0])

    def getMinor(self):
        ver = __version__.split('.')
        assert len(ver) >= 3
        return int(ver[2])

