import os
import sys


def get_command_output():
    command = """openstack aggregate show {} -c hosts -f value"""
    if len(args) == 2:
        cmd_res_1 = os.popen(command.format(args[1])).read()
        return list(eval(cmd_res_1.strip()))

    elif len(args) == 3:
        cmd_res_1 = os.popen(command.format(args[1])).read()
        list_1 = list(eval(cmd_res_1.strip()))

        cmd_res_2 = os.popen(command.format(args[2])).read()
        list_2 = list(eval(cmd_res_2.strip()))

        return [value for value in list_2 if value in list_1]


if __name__ == '__main__':
    args = sys.argv
    with open(file='/var/tmp/temp_input.txt', mode='w') as _write:
        result = get_command_output()
        for x in range(len(result)+1):
            if x == 0:
                _write.write(str(args[1]))
            else:
                _write.write(str(result[x-1]))
