import inspect

from globus_compute_sdk import Executor, Client
from custom_image_builder.exception.ImageBuilderException import ImageBuilderException
from custom_image_builder.exception.RegisterImageException import RegisterImageException


def funcx_build_image(image_file_name: str,
                      base_image_type: str,
                      base_image: str,
                      payload_url: str,
                      pip_packages: list,
                      conda_packages: list,
                      apt_packages: list) -> (str, str):
    """Builds apptainer/singularity image on HPC cluster using funcX, return path of the image and logs

    :param apt_packages:
    :param conda_packages:
    :param pip_packages:
    :param payload_url:
    :param base_image:
    :param image_file_name:
    :param base_image_type:
    :return: logs, path_of_image
    """
    from jinja2 import Template
    import subprocess
    import os

    build_file = """BootStrap: {{ container_type }}
From: {{ base_image }}

%post
    {% if apt is not none and apt|length > 0 %}
        {% for package in apt %}
        apt-get install {{ package }}
        {% endfor %}
    {% endif %}

    {% if payload_url is not none %}
        git clone {{payload_url }}
    {% endif %}

    {% if pip is not none and pip|length > 0 %}
        {% for package in pip %}
        pip install {{ package }}
        {% endfor %}
    {% endif %}

    {% if conda is not none and conda|length > 0 %}
        {% for package in conda %}
        conda install {{ package }}
        {% endfor %}
    {% endif %}
    
    pip install globus-compute-endpoint==2.2.0
    pip install globus-compute-common==0.2.0

%runscript
    """

    template_str = Template(build_file)

    build_file = template_str.render({
        "container_type": base_image_type,
        "base_image": base_image,
        "payload_url": payload_url,
        "pip": pip_packages,
        "apt": apt_packages,
        "conda": conda_packages
    })

    build_image_file_name = image_file_name
    open(f"{build_image_file_name}.def", "w").write(build_file)

    process = subprocess.Popen(
        f"apptainer build --force {build_image_file_name}.sif {build_image_file_name}.def",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )

    exit_code = process.wait()
    stdout, stderr = process.communicate()

    return f"Output logs are as follows: \n {str(stderr)}  \n {str(stdout)}", f"{os.getcwd()}/{build_image_file_name}.sif", exit_code


def register_container(image_file_path, gcc):
    try:
        # Register sif file path, created after successfully building the image
        container_id = gcc.register_container(image_file_path, "singularity")

        return container_id

    except Exception as ex:
        raise RegisterImageException(ex)

def redef_in_main(obj):
    """Helper: redefine an object in __main__

    This has the effect of coaxing dill into serializing both the definition and
    the instance of an object together (in the case of a class), so it can be
    deserialized without needing the definition to be available for import on
    the other side. We do this for the "real" function we register, too (see below)
    in order to guarantee that there are no intra-garden references that dill might
    try to import on the other end.

    This works because dill is smart enough to know that if you defined a class
    interactively (like in a repl) then it can't expect that definition to be
    available after the session exits, so has to include it.
    """

    # make sure it's not already in main
    if obj.__module__ != "__main__":
        import __main__

        s = inspect.getsource(obj)
        exec(s, __main__.__dict__)

def build_image(gc_executor: Executor,
                image_file_name: str,
                base_image_type: str,
                base_image: str,
                payload_url: str,
                pip_packages: list,
                conda_packages: list,
                apt_packages: list) -> str:
    """Calls Globus compute executor which Builds apptainer/singularity image on HPC cluster using funcX, return path of the image and logs

    :param gc_executor:
    :param apt_packages:
    :param conda_packages:
    :param pip_packages:
    :param payload_url:
    :param base_image:
    :param image_file_name:
    :param base_image_type:
    :return: image_file_path
    """
    import __main__

    try:
        with gc_executor as ex:
            redef_in_main(funcx_build_image)
            fut = ex.submit(__main__.funcx_build_image,
                                     image_file_name,
                                     base_image_type,
                                     base_image,
                                     payload_url,
                                     pip_packages,
                                     conda_packages,
                                     apt_packages)

        logs, image_file_path, exit_code = fut.result()

        if exit_code != 0:
            raise ImageBuilderException(f"Failed to build image,  {logs}")

        return image_file_path
    except Exception as ex:
        raise ImageBuilderException(ex)


def build_and_register_container(gcc_client: Client,
                                 endpoint_id: str,
                                 image_file_name: str,
                                 base_image_type: str,
                                 base_image: str,
                                 payload_url: str = None,
                                 pip_packages: list = None,
                                 conda_packages: list = None,
                                 apt_packages: list = None) -> str:
    """Calls Globus compute executor and client which Builds apptainer/singularity image on HPC cluster using funcX, and
    registers the image returning the container id

        :param gcc_client:
        :param endpoint_id:
        :param apt_packages:
        :param conda_packages:
        :param pip_packages:
        :param payload_url:
        :param base_image:
        :param image_file_name:
        :param base_image_type:
        :return: container_id """
    gc_executor = Executor(endpoint_id=endpoint_id, funcx_client=gcc_client)

    image_file_path = build_image(gc_executor,
                                  image_file_name,
                                  base_image_type,
                                  base_image,
                                  payload_url,
                                  pip_packages,
                                  conda_packages,
                                  apt_packages)

    return register_container(image_file_path, gcc_client)
