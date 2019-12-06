# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from subprocess import Popen, PIPE

def PrepCmd(key):
    """
    Prepare and return a shell command
    """
    cmd = ''
    features = {'SMMU'          : '/sys/kernel/debug/12000000.iommu',
                'SMMU_CLIENTS'  : '/sys/kernel/debug/12000000.iommu/masters',
                'VPR_RESIZE'    : '/sys/kernel/debug/dma-vpr/curr_size',
                'CMA'           : '/sys/kernel/debug/dma-vpr/cma_size',
                'ZRAM'          : '/sys/block/zram0',
                'HMM'           : 'proc/devices',
                'CVNAS'         : '/sys/kernel/debug/bpmp/debug/clk/clk_tree',
                'KMEMLEAK'      : '/sys/kernel/debug/kmemleak',
                'TRANSHUGEPAGE' : '/sys/kernel/mm/transparent_hugepage/enabled',
                'NVMAP'         : '/sys/kernel/debug/nvmap',
                'IO_COHERENCY'  : '/proc/device-tree/ -name dma-coherent',
                'L3_CACHE'      : '/sys/kernel/debug/l3_cache'
               }

    if key == 'SMMU' or key == 'ZRAM' or key == 'SMMU_CLIENTS' or key == 'KMEMLEAK' or key == 'NVMAP' or key == 'L3_CACHE':
        cmd = 'ls ' + features[key]
    elif key == 'VPR_RESIZE' or key == 'CMA' or key == 'HMM' or key == 'CVNAS' or key == 'TRANSHUGEPAGE':
        cmd = 'cat ' + features[key]
    elif key == 'IO_COHERENCY':
        cmd = 'find ' + features[key]
    else:
        return key
    return cmd

def RunCmd(key):
    """
    Runs a shell command and returns output in stdout and stderr
    """
    cmd = PrepCmd(key)
    try:
        process = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
    except Exception, e:
        print "Error : " + str(e)

    return stdout, stderr

def PrintFeature(result):
    """
    Prints whether a feature is enabled/disabled
    """
    if not result:
        print "Enabled"
    else:
        print "Disabled"

def PrintClients(client):
    """
    Print clients in formatted way
    """
    i = 0
    while i < len(client):
        print ("%20s " % client[i]),
        i += 1
        if i%4 == 0:
            print ""
    print ""

def PrintLine():
    """
    Prints line to seperate modules in output
    """
    for i in range(0, 50):
        print ("-"),
