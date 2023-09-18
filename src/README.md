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



## Example

Consider the following use-case where the user wants to execute a pandas operation on HPC using globus-compute.
They need a singularity image which would be used by the globus-compute executor. The library can be leveraged as follows:
```python
from custom_image_builder import build_and_register_container

tutorial_endpoint = "01e21ddf-6eb4-41db-8e1d-2bcfe0c8314f"
container_id = build_and_register_container(endpoint_id=tutorial_endpoint,
                                            image_file_name="my-test-image", 
                                            base_image_type="docker", 
                                            base_image="python:3.8",
                                            pip_packages=["pandas"])

print("Container id ", container_id)

from globus_compute_sdk import Executor

# User function runs on the HPC node
def transform():
    import pandas as pd
    data = {
        'City': ['New York', 'San Francisco', 'Los Angeles']
    }
    return pd.DataFrame(data)


with Executor(endpoint_id=tutorial_endpoint,
              container_id=container_id) as ex:
    fut = ex.submit(transform)
    

print(fut.result())

```
