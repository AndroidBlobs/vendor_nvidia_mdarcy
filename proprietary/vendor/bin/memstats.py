""":"; exec python "$0" "$@" ;" """
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

__doc__ = """memstats.py: tool for memory information"""

import os
import sys
import time
from nvmap_stats import nvmap_stats
from smmu_stats import smmu_stats
from vpr_stats import vpr_stats, get_vpr_runtime
from common import RunCmd, PrintLine, PrintFeature, PrintClients

COHERENCY_CLIENTS = []
SOC = ''
OS = ''

def print_help():
    """
    Print usage of memstats
    """
    print "\nUsage: memstats.py [-h] [--vpr] [--nvmap] [--smmu]\n"
    print "This program is used to generate a Memory Breakdown Analysis."
    print "optional arguments:"
    print "\t-h, --help      show this help message and exit"
    print "\t    --all       Display all memory related information."
    print "\t    --vpr       Display VPR information."
    print "\t    --smmu      Display SMMU clients information."
    print "\t    --nvmap     Display NvMap information."
    print "\t    --runtime   Continously print memory summary"

def get_OS():
    """
    Try to get OS on which memstats is running
    """
    data, err = RunCmd("cat /sbin/adbd")
    if not err:
        return 'Android'

    if os.path.exists('/proc/boot/fs-qnx6.so') or os.path.exists('/proc/boot/mkqnx6fs'):
        return 'QNX'

    data, err = RunCmd("cat /etc/lsb-release")
    if not err:
        if data.find("CHROMEOS_RELEASE_NAME=Chromium OS") != -1:
            return 'ChromeOS'

    return 'Linux'

def runtime(interval):
    """
    Continously print memory summary
    """
    while True:
        print "\n\n"
        temp = memtotal = memfree = memavailable = nvmapused = nvmapfree = cmatotal = cmafree = SwapTotal = SwapFree = ''
        data, err = RunCmd('cat /proc/meminfo')
        meminfo = data.split('\n')
        for temp in meminfo:
            if 'MemTotal' in temp:
                memtotal = temp.split(':')[1].strip()
            elif 'NvMapMemFree' in temp:
                nvmapfree = temp.split(':')[1].strip()
            elif 'MemFree' in temp:
                memfree = temp.split(':')[1].strip()
            elif 'MemAvailable' in temp:
                memavailable = temp.split(':')[1].strip()
            elif 'NvMapMemUsed' in temp:
                nvmapused = temp.split(':')[1].strip()
            elif 'CmaTotal' in temp:
                cmatotal = temp.split(':')[1].strip()
            elif 'CmaFree' in temp:
                cmafree = temp.split(':')[1].strip()
            elif 'SwapTotal' in temp:
                SwapTotal = temp.split(':')[1].strip()
            elif 'SwapFree' in temp:
                SwapFree = temp.split(':')[1].strip()

        vpr_total, curr_alloc, vpr_floor = get_vpr_runtime()
        print ("Memory [Total:" + memtotal + " Free:" + memfree + " Available:" + memavailable + "]"),
        print ("NvMap [Used:" + nvmapused + " Free:" + nvmapfree + "]"),
        print ("CMA [Total:" + cmatotal + " Free:" + cmafree + "]"),
        print ("VPR [Total:" + str(vpr_total) + "kB CurrAlloc:" + str(curr_alloc) + "kB FloorSize:" + str(vpr_floor) + "kB]"),
        print "ZRAM [Total:" + SwapTotal + " Free:" + SwapFree + "]"
        sys.stdout.flush()
        time.sleep(interval/1000)

def MemoryFeatures():
    """
    Check various memory features are enabled/disabled for current device
    """
    global COHERENCY_CLIENTS
    global SOC

    print "-----------Memory Features------------"

    print ("SMMU\t\t: "),
    data, err = RunCmd('SMMU')
    PrintFeature(err)

    print ("VPR resize\t: "),
    data, err = RunCmd('VPR_RESIZE')
    PrintFeature(err)

    print ("CMA\t\t: "),
    data, err = RunCmd('CMA')
    if not err:
        cma_size = int(data, 16)
        PrintFeature(cma_size == 0)
    else:
        PrintFeature(True)

    print ("ZRAM\t\t: "),
    data, err = RunCmd('ZRAM')
    PrintFeature(err)

    print ("HMM\t\t: "),
    data, err = RunCmd('HMM')
    if not err:
        PrintFeature(data.find("hmm") == -1)
    else:
        PrintFeature(True)

    print ("CVNAS\t\t: "),
    data, err = RunCmd('CVNAS')
    if not err:
        PrintFeature(data.find("cvnas") == -1)
    else:
        PrintFeature(True)

    print ("kmemleak\t: "),
    data, err = RunCmd('KMEMLEAK')
    PrintFeature(err)

    print ("TransHugePage\t: "),
    data, err = RunCmd('TRANSHUGEPAGE')
    if not err:
        PrintFeature(data.find("[never]") != -1)
    else:
        PrintFeature(True)

    print ("Nvmap\t\t: "),
    data, err = RunCmd('NVMAP')
    PrintFeature(err)

    print ("IO coherency\t: "),
    data, err = RunCmd('IO_COHERENCY')
    if data:
        lines = data.split("\n")
        for line in lines:
            if line:
                COHERENCY_CLIENTS.append(line.split("/")[-2])
    PrintFeature(not data)

    print ("L3 Cache\t: "),
    if SOC == "tegra186" or SOC == "tegra210" or SOC == "tegra214":
        print "NotPresent"
    else:
        data, err = RunCmd('L3_CACHE')
        PrintFeature(err)

def MemoryUsage():
    """
    Check memory usage for current device
    """

    global COHERENCY_CLIENTS

    print "-----------Memory Usage---------------"

    print "Meminfo (/proc/meminfo) :"
    data, err = RunCmd("cat /proc/meminfo")
    if not err:
        print data
    else:
        print "Failed to get meminfo"
        print "Stderr : "+ err

    PrintLine()

    if OS == 'Android':
        print "\nProcrank :"
        data, err = RunCmd("procrank")
        if not err or data:
            print data
        else:
            print "Failed run Procrank"
            print "Stderr : "+ err

    if os.path.exists("/sys/kernel/debug/l3_cache"):
        PrintLine()
        print "\nL3 Cache :"
        data, err = RunCmd("cat /sys/kernel/debug/l3_cache/gpu_cpu_ways")
        if not err:
            print "gpu_cpu_ways\t: " + data.rstrip()
        data, err = RunCmd("cat /sys/kernel/debug/l3_cache/gpu_only_ways")
        if not err:
            print "gpu_only_ways\t: " + data.rstrip()
        data, err = RunCmd("cat /sys/kernel/debug/l3_cache/size")
        if not err:
            print "Size\t\t: " + data.rstrip() + " bytes"
        data, err = RunCmd("cat /sys/kernel/debug/l3_cache/total_ways")
        if not err:
            print "total_ways\t: " + data.rstrip()

    if COHERENCY_CLIENTS:
        PrintLine()
        print "\nIO-Coherency Clients :"
        PrintClients(COHERENCY_CLIENTS)

def Memstats():
    """
    Main fucntion which will print general info and invoke other functions
    """
    print "=========Nvidia Tegra Memstats========="

    global SOC
    global OS

    print ("Device\t\t\t: "),
    data, err = RunCmd("cat /proc/device-tree/compatible")
    if not err:
        SOC = data.split(",")[-1].strip()[:-1]
        board = data.split(",")[1]
        print SOC + ", " + board[:-6]
    else:
        print "Failed to get device details"
        print "Stderr : "+ err

    print ("Linux Kernel Version\t: "),
    data, err = RunCmd("cat /proc/version")
    if not err:
        print data.split("-")[0].split(" ")[-1]
    else:
        print "Failed to get version"
        print "Stderr : "+ err

    print ("OS\t\t\t: "),
    OS = get_OS()
    print OS

    MemoryFeatures()
    MemoryUsage()

if len(sys.argv) > 1:
    arg = sys.argv[1].lstrip('-')
    if arg == 'help' or arg == 'h':
        print_help()
        exit()

    Memstats()
    PrintLine()
    arg = sys.argv[1].lstrip('-')
    if arg == 'nvmap':
        nvmap_stats()
    elif arg == 'smmu':
        if len(sys.argv) == 3:
            smmu_stats(sys.argv[2])
        else:
            smmu_stats('')
    elif arg == 'vpr':
        vpr_stats()
    elif arg == 'all':
        nvmap_stats()
        PrintLine()
        smmu_stats('')
        PrintLine()
        vpr_stats()
    elif arg == 'runtime':
        nvmap_stats()
        PrintLine()
        smmu_stats('')
        PrintLine()
        vpr_stats()
        PrintLine()
        if len(sys.argv) == 3:
            runtime(int(sys.argv[2]))
        else:
            runtime(3000)
    else:
        print "Unknown Argument!"
else:
    Memstats()
    PrintLine()
    nvmap_stats()
    PrintLine()
    smmu_stats('')
    PrintLine()
    vpr_stats()
