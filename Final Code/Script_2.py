import paramiko
from prettytable import PrettyTable


def run_cmd(host):
    numa_node_cpus = []
    vcpupin_set = []
    numa_node_cpus_available_for_vms = []
    running_vm_instances = []
    cores_utilized_by_vm = {}
    total_core_utilized_by_vms = []
    utilization_by_nodes = []

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname=host)

    for idx in range(4):
        if idx == 0:
            command_1 = 'lscpu | grep -i numa | grep -i cpu'
            std_in, std_out, std_err = client.exec_command(command=command_1)
            out = std_out.readlines()
            # print('command_1', command_1, 'out:', out)

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

            numa_node_cpus_available_for_vms = [[] for _ in range(len(numa_node_cpus))]
            utilization_by_nodes = [[] for _ in range(len(numa_node_cpus))]

            # print('0 numa_node_cpus:', numa_node_cpus)

        elif idx == 1:
            command_2 = '/usr/bin/sudo -H /usr/localcw/bin/eksh -c "cat /etc/nova/nova.conf | grep -i set | grep -v ^#"'
            std_in, std_out, std_err = client.exec_command(command=command_2)
            out = std_out.readlines()
            # print('command_2', command_2, 'out:', out)
            if out:
                vcpupin_set = out[0].split('=')[1].strip().split(',')

            for x in vcpupin_set:
                for y in range(len(numa_node_cpus)):
                    if x in numa_node_cpus[y]:
                        numa_node_cpus_available_for_vms[y].append(x)

            # print('1 numa_node_cpus_available_for_vms:', numa_node_cpus_available_for_vms)

        elif idx == 2:
            command_3 = 'virsh list --all'
            std_in, std_out, std_err = client.exec_command(command=command_3)
            out = std_out.readlines()
            # print('command_3', command_3, 'out:', out)

            if out:
                for x in out:
                    if 'instance' in x and 'running' in x:
                        instance = x.replace(' ', '').strip().split('-')
                        inst = instance[0][1:] + '-' + instance[1].replace('running', '')
                        running_vm_instances.append(inst)

            # print('2 running_vm_instances:', running_vm_instances)

        elif idx == 3:
            for _inst in running_vm_instances:
                command_4 = 'virsh vcpupin {}'.format(_inst)
                std_in, std_out, std_err = client.exec_command(command=command_4)
                out = std_out.readlines()
                # print('command_4', command_4, 'out:', out)

                if out:
                    res = []
                    for _id, x in enumerate(out):
                        if _id >= 2 and '-' not in x and x.strip() != '':
                            core = x.split(':')[1].strip()
                            res.append(core)
                            if core not in total_core_utilized_by_vms:
                                total_core_utilized_by_vms.append(core)
                    cores_utilized_by_vm[_inst] = res

            # print('3 total_core_utilized_by_vms:', total_core_utilized_by_vms)
            # print('3 cores_utilized_by_vm:', cores_utilized_by_vm)

    client.close()

    for val1 in total_core_utilized_by_vms:
        for _node in range(len(numa_node_cpus_available_for_vms)):
            if val1 in numa_node_cpus_available_for_vms[_node]:
                utilization_by_nodes[_node].append(val1)

    # print('4 utilization_by_nodes:', utilization_by_nodes)

    utilization_per_node = ['{}/{}'.format(len(utilization_by_nodes[x]), len(numa_node_cpus_available_for_vms[x]))
                            for x in range(len(utilization_by_nodes))]

    return utilization_per_node



if __name__ == '__main__':
    with open(file='/var/tmp/temp_input.txt', mode='w') as data:
        az = data.readlines()[0]
        print('az:', az)
        source_data = [_data.strip() for _data in list(data.readlines())[1:]]

        final_response = [[] for _ in range(len(source_data))]
        for _index, (_host, _zone) in enumerate(source_data):
            response = run_cmd(_host.strip())
            Used_Node0, Total_node0 = response[0].split('/')
            Used_Node1, Total_node1 = response[1].split('/')
            final_response[_index] = [_host, _zone, Total_node0, Used_Node0, int(Total_node0) - int(Used_Node0),
                                      Total_node1,
                                      Used_Node1, int(Total_node1) - int(Used_Node1)]

        table = PrettyTable()
        table.field_names = ['Hostname', 'AZ', 'Total_node0', 'Used_Node0', 'Free_Node0', 'Total_node1', 'Used_Node1',
                             'Free_Node1']
        for val in final_response:
            table.add_row([val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7]])

        print(table)
