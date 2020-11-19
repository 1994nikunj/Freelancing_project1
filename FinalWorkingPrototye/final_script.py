import os
import sys

import paramiko
from prettytable import PrettyTable

args = sys.argv


def get_command_output():
    command = """openstack aggregate show {} -c hosts -f value"""
    _data = None

    try:
        if len(args) == 2:
            cmd_res_1 = os.popen(command.format(args[1])).read()
            _data = list(eval(cmd_res_1.strip()))

        elif len(args) == 3:
            cmd_res_1 = os.popen(command.format(args[1])).read()
            list_1 = list(eval(cmd_res_1.strip()))

            cmd_res_2 = os.popen(command.format(args[2])).read()
            list_2 = list(eval(cmd_res_2.strip()))

            _data = [value for value in list_2 if value in list_1]

    except Exception as e:
        print('Exception Caught: {}'.format(e))
        sys.exit(0)

    else:
        return _data


def run_cmd(host):
    node0_full = 0
    node0_free = 0
    node1_full = 0
    node1_free = 0
    numa_node_cpus = []
    vcpupin_set = []
    numa_node_cpus_available_for_vms = []
    running_vm_instances = []
    cores_utilized_by_vm = {}
    total_core_utilized_by_vms = []
    utilization_by_nodes = []

    try:
        VAR1 = 0
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=host,
                       allow_agent=False)

    except Exception as e:
        print('Exception Caught: {}'.format(e))
        sys.exit(0)

    else:
        for idx in range(8):
            if idx == 0:
                cmd_1 = 'lscpu | grep -i numa | grep -i cpu'
                std_in, std_out, std_err = client.exec_command(command=cmd_1)
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
                cmd_2 = '/usr/bin/sudo -H /usr/localcw/bin/eksh -c "cat /etc/nova/nova.conf | grep -i set | grep -v ^#"'
                std_in, std_out, std_err = client.exec_command(command=cmd_2)
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
                cmd_3 = 'virsh list --all'
                std_in, std_out, std_err = client.exec_command(command=cmd_3)
                out = std_out.readlines()
                # print('command_3', command_3, 'out:', out)

                if out:
                    for x in out:
                        if 'instance' in x and 'running' in x:
                            # instance = x.replace(' ', '').strip().split('-')
                            # inst = instance[0][1:] + '-' + instance[1].replace('running', '')
                            inst = x.split()[1]
                            running_vm_instances.append(inst)
                # print('2 running_vm_instances:', running_vm_instances)

            elif idx == 3:
                for _inst in running_vm_instances:
                    cmd_4 = 'virsh vcpupin {}'.format(_inst)
                    std_in, std_out, std_err = client.exec_command(command=cmd_4)
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

            elif idx == 4:
                cmd_5 = '/usr/bin/sudo -H /usr/localcw/bin/eksh -c "cat /sys/devices/system/node/node0/hugepages/hugepages-*/nr_hugepages"'
                std_in, std_out, std_err = client.exec_command(command=cmd_5)
                out = std_out.readlines()
                node0_full = str(out[0]).strip()

            elif idx == 5:
                cmd_6 = '/usr/bin/sudo -H /usr/localcw/bin/eksh -c "cat /sys/devices/system/node/node0/hugepages/hugepages-*/free_hugepages"'
                std_in, std_out, std_err = client.exec_command(command=cmd_6)
                out = std_out.readlines()
                node0_free = str(out[0]).strip()

            elif idx == 6:
                cmd_7 = '/usr/bin/sudo -H /usr/localcw/bin/eksh -c "cat /sys/devices/system/node/node1/hugepages/hugepages-*/nr_hugepages"'
                std_in, std_out, std_err = client.exec_command(command=cmd_7)
                out = std_out.readlines()
                node1_full = str(out[0]).strip()

            elif idx == 7:
                cmd_8 = '/usr/bin/sudo -H /usr/localcw/bin/eksh -c "cat /sys/devices/system/node/node1/hugepages/hugepages-*/free_hugepages"'
                std_in, std_out, std_err = client.exec_command(command=cmd_8)
                out = std_out.readlines()
                node1_free = str(out[0]).strip()

    client.close()

    for val1 in total_core_utilized_by_vms:
        for _node in range(len(numa_node_cpus_available_for_vms)):
            if val1 in numa_node_cpus_available_for_vms[_node]:
                utilization_by_nodes[_node].append(val1)
    # print('4 utilization_by_nodes:', utilization_by_nodes)

    # print('numa_node_cpus', numa_node_cpus)
    # print('vcpupin_set', vcpupin_set)
    # print('numa_node_cpus_available_for_vms', numa_node_cpus_available_for_vms)
    # print('running_vm_instances', running_vm_instances)
    # print('cores_utilized_by_vm', cores_utilized_by_vm)
    # print('total_core_utilized_by_vms', total_core_utilized_by_vms)
    # print('utilization_by_nodes', utilization_by_nodes)

    final_resp = []
    for x in range(len(utilization_by_nodes)):
        if x == 0:
            final_resp.append([
                len(numa_node_cpus_available_for_vms[x]),
                len(utilization_by_nodes[x]),
                node0_full,
                node0_free])
        elif x == 1:
            final_resp.append([
                len(numa_node_cpus_available_for_vms[x]),
                len(utilization_by_nodes[x]),
                node1_full,
                node1_free])

    final_resp.append(len(running_vm_instances))

    return final_resp


if __name__ == '__main__':
    _zone = None
    if len(args) == 2:
        _zone = args[1]
    elif len(args) == 3:
        _zone = '%s, %s' % (args[1], args[2])

    data = get_command_output()
    # print('Data:', data)
    source_data = [_data.strip() for _data in list(data)]
    final_response = [[] for _ in range(len(source_data))]

    for _index, _host in enumerate(source_data):
        rs = run_cmd(_host.strip())
        # print('Final Response:', rs)
        final_response[_index] = [_host, _zone,
                                  rs[0][0], rs[0][1], int(rs[0][0]) - int(rs[0][1]),
                                  rs[1][0], rs[1][1], int(rs[1][0]) - int(rs[1][1]),
                                  rs[2],
                                  rs[0][2], rs[0][3], rs[1][2], rs[1][3]]

    table = PrettyTable()
    table.field_names = ['Hostname', 'AZ', 'ActiveVM',
                         'N0_Total', 'N0_Used', 'N0_Free',
                         'N1_Total', 'N1_Used', 'N1_Free',
                         'HG0_Total', 'HG0_Free', 'HG1_Total', 'HG1_Free']

    for val in final_response:
        table.add_row([val[0], val[1], val[8],
                       val[2], val[3], val[4],
                       val[5], val[6], val[7],
                       val[9], val[10], val[11], val[12]])

    print(table)
