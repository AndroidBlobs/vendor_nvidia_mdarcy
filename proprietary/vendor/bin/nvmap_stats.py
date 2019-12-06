# Copyright (c) 2018, NVIDIA CORPORATION.  All Rights Reserved.
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited

from common import RunCmd, PrintLine

def nvmap_stats():
    """
    Dump nvmap related information from nvmap debugfs
    """

    print "\n---------------NvMap Usage---------------"
    print "Procrank :"
    data, err = RunCmd("cat /sys/kernel/debug/nvmap/iovmm/procrank")
    if not err:
        print data
    else:
        print "Stderr : " + err

    PrintLine()
    print "\nOrphan handles :"
    data, err = RunCmd("cat /sys/kernel/debug/nvmap/iovmm/orphan_handles")
    if not err:
        print data
    else:
        print "Stderr : " + err

    PrintLine()
    print "\nMaps :"
    data, err = RunCmd("cat /sys/kernel/debug/nvmap/iovmm/maps")
    if not err:
        print data
    else:
        print "Stderr : " + err

    PrintLine()
    print "\nPagepool :"
    data, err = RunCmd("ls /sys/kernel/debug/nvmap/pagepool")
    if not err:
        for line in data.split():
            if line:
                data, err = RunCmd("cat /sys/kernel/debug/nvmap/pagepool/" + line)
                print line + " = " + data.strip()
    else:
        print "Stderr : " + err
