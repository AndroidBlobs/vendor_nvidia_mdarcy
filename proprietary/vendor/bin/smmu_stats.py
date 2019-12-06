# Copyright (c) 2018, NVIDIA CORPORATION.  All Rights Reserved.
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited

from common import RunCmd, PrintClients, PrintLine

def smmu_stats(client):
    """
    Read and dump smmu related things
    """
    smmu_clients = []
    data, err = RunCmd('SMMU')
    if not err:
        data, err = RunCmd('SMMU_CLIENTS')
        if data:
            for line in data.split("\n"):
                if line:
                    smmu_clients.append(line)

    if smmu_clients:
        print "\n---------------SMMU Clients---------------"
        PrintClients(smmu_clients)

    if client:
        PrintLine()
        data, err = RunCmd("find -L /d/12000000.iommu/masters/" + client + " -name ptdump")
        if data:
            iova, err = RunCmd("cat " + data.strip())
            if not err:
                print "\n" + client + " IOVA mappings :"
                print iova
            else:
                print "Stderr : " + err
        else:
            print "\n" + client + " : No such client!"
