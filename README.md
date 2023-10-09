# Building a singular container for HPC using globus-compute

## Context
* One of the execution configurations of [globus-compute](https://www.globus.org/compute) requires a registered container which is spun up to execute the user function on the HPC.

* HPCs do not run docker containers(due to security reasons as discussed [here](https://docs.vscentrum.be/software/singularity.html)) and support only an apptainer/singularity image.

* Installing the apptainer setup to build the singularity image locally is not a straightforward process especially on windows and mac systems as discussed in the [documentation](https://apptainer.org/docs/admin/main/installation.html).

Using this python library the user can specify their custom image specification to build an apptainer/singularity image 
which would be used to in-turn to run their functions on globus-compute. The library registers the container and 
returns the container id which would be used by the globus-compute executor to execute the user function.


## Prerequisite.
A [globus-compute-endpoint](https://globus-compute.readthedocs.io/en/latest/endpoints.html) setup on HPC cluster.

The following steps can be used to create an endpoint on the NCSA Delta Cluster, you can modify the configurations based on your use-case:

1. Create a conda virtual env. We have created a ```custom-image-builder``` conda env on the delta cluster as follows:
```shell
conda create --name custom-image-builder python=3.11

conda activate custom-image-builder

pip install globus-compute-endpoint==2.2.0

pip install custom-image-builder
```

2. Creating a globus-compute endpoint:

```shell
globus-compute-endpoint configure custom-image-builder
```

Update the endpoint config at ```~/.globus_compute/custom-image-builder/config.py``` to :
```python

from parsl.addresses import address_by_interface
from parsl.launchers import SrunLauncher
from parsl.providers import SlurmProvider

from globus_compute_endpoint.endpoint.utils.config import Config
from globus_compute_endpoint.executors import HighThroughputExecutor


user_opts = {
    'delta': {
        'worker_init': 'conda activate custom-image-builder',
        'scheduler_options': '#SBATCH --account=bbmi-delta-cpu',
    }
}

config = Config(
    executors=[
        HighThroughputExecutor(
            max_workers_per_node=10,
            address=address_by_interface('hsn0'),
            scheduler_mode='soft',
            worker_mode='singularity_reuse',
            container_type='singularity',
            container_cmd_options="",
            provider=SlurmProvider(
                partition='cpu',
                launcher=SrunLauncher(),

                # string to prepend to #SBATCH blocks in the submit
                # script to the scheduler eg: '#SBATCH --constraint=knl,quad,cache'
                scheduler_options=user_opts['delta']['scheduler_options'],
                worker_init=user_opts['delta']['worker_init'],
                # Command to be run before starting a worker, such as:
                # 'module load Anaconda; source activate parsl_env'.

                # Scale between 0-1 blocks with 2 nodes per block
                nodes_per_block=1,
                init_blocks=0,
                min_blocks=0,
                max_blocks=1,

                # Hold blocks for 30 minutes
                walltime='00:30:00'
            ),
        )
    ],
)
```

3. Start the endpoint and store the endpoint id to be used in the following example

```shell
globus-compute-endpoint start custom-image-builder
```


## Example

Consider the following use-case where the user wants to execute a pandas operation on HPC using globus-compute.
They need a singularity image which would be used by the globus-compute executor. The library can be leveraged as follows:

Locally you need to install the following packages, you can create a virtual env as follows:


```shell
cd example/

python3.9 -m venv venv

source venv/bin/activate

pip install globus-compute-sdk==2.2.0

pip install custom-image-builder
```


```python
from custom_image_builder import build_and_register_container
from globus_compute_sdk import Client, Executor


def transform():
    import pandas as pd
    data = {'Column1': [1, 2, 3],
            'Column2': [4, 5, 6]}

    df = pd.DataFrame(data)

    return "Successfully created df"


def main():
    image_builder_endpoint = "81b21a94-0e18-457d-98b5-05672a8a3b60"
    gcc_client = Client()

    container_id = build_and_register_container(gcc_client=gcc_client,
                                                endpoint_id=image_builder_endpoint,
                                                image_file_name="my-pandas-image",
                                                base_image_type="docker",
                                                base_image="python:3.8",
                                                pip_packages=["pandas"])

    print("The container id is", container_id)

    example_endpoint = "0b4e042b-edd5-4951-9ce5-6608c2ef6cb8"

    with Executor(endpoint_id=example_endpoint,
                  container_id="791a75b4-c2bd-40f1-85e0-ba17458c233b") as ex:
        fut = ex.submit(transform)

    print(fut.result())
```


## Note.
For the following example to work we must use the globus-compute-sdk version of 2.2.0 while setting up our endpoint.

The singularity image require globus-compute-endpoint as one of its packages in-order to run the workers as our custom 
singularity container, hence by default we require python as part of the image inorder to install globus-compute-endpoint. 
