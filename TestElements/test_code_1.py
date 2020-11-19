from prettytable import PrettyTable

if __name__ == '__main__':
    numa_node_cpus = []
    vcpupin_set = []
    numa_node_cpus_available_for_vms = []
    running_vm_instances = []
    cores_utilized_by_vm = {}
    total_core_utilized_by_vms = []
    utilization_by_nodes = []

    for idx in range(4):
        if idx == 0:
            out = [u'NUMA node0 CPU(s):     0-13,28-41\n',
                   u'NUMA node1 CPU(s):     14-27,42-55\n']

            if out:
                for ind, x in enumerate(out):
                    if '-' in x:
                        node = x.split(':')[1].strip()
                        aa = [list(range(int(x.split('-')[0]), int(x.split('-')[1]) + 1)) for x in node.split(',')]
                        ab = []
                        for x1 in aa:
                            for x2 in x1:
                                ab.append(str(x2))
                        numa_node_cpus.append(ab)
                    else:
                        node = x.split(':')[1].strip().split(',')
                        numa_node_cpus.append(node)

            utilization_by_nodes = [[] for _ in range(len(numa_node_cpus))]
            numa_node_cpus_available_for_vms = [[] for _ in range(len(numa_node_cpus))]

        elif idx == 1:
            out = ['vcpupin_set=4,6,8,10,12,14,16,22,24,26,28,30,5,7,11,13,15,17,19,23,25,27,29,31']
            if out:
                vcpupin_set = out[0].split('=')[1].strip().split(',')

            for x in vcpupin_set:
                for y in range(len(numa_node_cpus)):
                    if x in numa_node_cpus[y]:
                        numa_node_cpus_available_for_vms[y].append(x)

        elif idx == 2:
            out = [u' Id    Name                           State\n',
                   u'----------------------------------------------------\n',
                   u' 2     instance-0000cea2              running\n',
                   u' 5     instance-00011985              running\n',
                   u' -     instance-0000caef              shut off\n', u'\n']
            if out:
                for x in out:
                    if 'instance' in x and 'running' in x:
                        # instance = x.replace(' ', '').strip().split('-')
                        # inst = instance[0][1:] + '-' + instance[1].replace('running', '')
                        inst = x.split()[2]
                        running_vm_instances.append(inst)

        elif idx == 3:
            out = ''
            for index, _inst in enumerate(running_vm_instances):
                if index == 0:
                    out = [u'VCPU: CPU Affinity\n',
                           u'----------------------------------\n',
                           u'   0: 4\n',
                           u'   1: 14\n',
                           u'   2: 6\n',
                           u'   3: 16\n',
                           u'\n']
                else:
                    out = [u'VCPU: CPU Affinity\n',
                           u'----------------------------------\n',
                           u'   0: 8\n',
                           u'   1: 22\n',
                           u'   2: 10\n',
                           u'   3: 24\n',
                           u'\n']

                if out:
                    res = []
                    for _id, x in enumerate(out):
                        if _id >= 2 and '-' not in x and x.strip() != '':
                            core = x.split(':')[1].strip()
                            res.append(core)
                            if core not in total_core_utilized_by_vms:
                                total_core_utilized_by_vms.append(core)
                    cores_utilized_by_vm[_inst] = res

    for val in total_core_utilized_by_vms:
        for _node in range(len(numa_node_cpus_available_for_vms)):
            if val in numa_node_cpus_available_for_vms[_node]:
                utilization_by_nodes[_node].append(val)

    print('cores_utilized_by_vm', cores_utilized_by_vm)
    print('numa_node_cpus_available_for_vms', numa_node_cpus_available_for_vms)
    print('utilization_by_nodes', utilization_by_nodes)

    final_resp = []
    for x in range(len(utilization_by_nodes)):
        final_resp.append([len(utilization_by_nodes[x]), len(numa_node_cpus_available_for_vms[x]), ])

    print(final_resp)
