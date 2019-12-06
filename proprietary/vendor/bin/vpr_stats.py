#Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import os
from common import RunCmd

def vpr_stats():
    """
    Print all vpr related info
    """
    if os.path.exists('/sys/kernel/debug/dma-vpr'):
        print "\nVPR usage :"
        data, err = RunCmd("cat /sys/kernel/debug/dma-vpr/cma_size")
        vpr_size = int(data, 16)
        if not err:
            print "Size\t\t\t: " + str(vpr_size/1024) + " kB"
        else:
            print "Failed to get VPR size"
            print "Stderr : "+ err
        data, err = RunCmd("cat /sys/kernel/debug/dma-vpr/cma_base")
        if not err:
            print "Range\t\t\t: " + hex(int(data.rstrip(), 16))[:-1] + " -- " + str(hex(int(data, 16) + vpr_size))[:-1]
        else:
            print "Failed to get VPR base"
            print "Stderr : "+ err
        data, err = RunCmd("cat /sys/kernel/debug/dma-vpr/curr_size")
        if not err:
            print "Current Allocation\t: " + str(int(data, 16)/1024) + " kB"
        else:
            print "Failed to get curr_size"
            print "Stderr : "+ err
        data, err = RunCmd("cat /sys/kernel/debug/dma-vpr/floor_size")
        if not err:
            print "Floor Size\t\t: " + str(int(data, 16)/1024) + " kB"
        else:
            print "Failed to get floor_size"
            print "Stderr : "+ err
        data, err = RunCmd("cat /sys/kernel/debug/dma-vpr/cma_chunk_size")
        if not err:
            print "Chunk Size\t\t: " + str(int(data, 16)/1024) + " kB"
        else:
            print "Failed to get floor_size"
            print "Stderr : "+ err

    print "\nNvMap VPR Usage :"
    data, err = RunCmd("cat /sys/kernel/debug/nvmap/vpr/clients")
    if not err:
        print data
    else:
        print "Failed to get NvMap VPR usage"
        print "Stderr : "+ err

    print "/proc/pagetypeinfo :"
    data, err = RunCmd("cat /proc/pagetypeinfo")
    if not err:
        print data
    else:
        print "Stderr : " + err

def get_vpr_runtime():
    """
    Return runtime VPR resize info
    """
    vpr_size = curr_alloc = vpr_floor = 0
    data, err = RunCmd("cat /sys/kernel/debug/dma-vpr/cma_size")
    if not err:
        vpr_size = int(data, 16)/1024
    data, err = RunCmd("cat /sys/kernel/debug/dma-vpr/curr_size")
    if not err:
        curr_alloc = int(data, 16)/1024
    data, err = RunCmd("cat /sys/kernel/debug/dma-vpr/floor_size")
    if not err:
        vpr_floor = int(data, 16)/1024

    return vpr_size, curr_alloc, vpr_floor
