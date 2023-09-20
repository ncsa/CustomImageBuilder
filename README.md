# Building a singular container for HPC using globus-compute

## Context
* One of the executions configurations of [globus-compute](https://www.globus.org/compute) requires a registered container which is spun up to execute the user function on the HPC.

* HPCs do not run docker containers(due to security reasons as discussed [here](https://docs.vscentrum.be/software/singularity.html)) and support only an apptainer/singularity image.

* Installing the apptainer setup to build the singularity image locally is not a straightforward process especially on windows and mac systems as discussed in the [documentation](https://apptainer.org/docs/admin/main/installation.html).

Using this python library the user can specify their custom image specification to build an apptainer/singularity image 
which would be used to in-turn to run their functions on globus-compute. The library registers the container and 
returns the container id which would be used by the globus-compute executor to execute the user function.


## Prerequisite.
A [globus-compute-endpoint](https://globus-compute.readthedocs.io/en/latest/endpoints.html) setup on HPC cluster.
In the following example the above endpoint would be your image builder endpoint.

You will need another endpoint to run your code in your custom container. You can refer the example_config.py to setup your endpoint.


## Example

Consider the following use-case where the user wants to execute a pandas operation on HPC using globus-compute.
They need a singularity image which would be used by the globus-compute executor. The library can be leveraged as follows:
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
