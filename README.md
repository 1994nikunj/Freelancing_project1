# Virtual Machine Core Utilization Monitoring

#### The code is connecting to a remote host via SSH using the paramiko library and retrieving information about the virtual machines running on that host. 
#### The information includes details about the virtual CPU pinning for each virtual machine, the cores utilized by each virtual machine, and the utilization of cores across NUMA nodes. 
#### This information is stored in various variables such as:
- numa_node_cpus, 
- vcpupin_set, 
- running_vm_instances, and 
- cores_utilized_by_vm. 
#### The code retrieves this information by executing various shell commands on the remote host and parsing the output. 
#### The data is collected in four stages and processed at each stage, with the final processed data stored in the above-mentioned variables.
