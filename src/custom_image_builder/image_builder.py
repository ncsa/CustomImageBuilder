from time import sleep
from globus_compute_sdk import Executor, Client

from custom_image_builder.exception.ImageBuilderException import ImageBuilderException
from custom_image_builder.exception.RegisterImageException import RegisterImageException


def funcx_build_image(image_file_name, base_image_type, base_image,
                      payload_url, pip_packages, conda_packages, apt_packages):
    """Builds apptainer/singularity image on Delta using funcX, return path of the image and logs

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

%runscript
    echo "----- Demo Image ----------"
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

    stdout, stderr = process.communicate()

    return f"Output logs are as follows: \n {str(stderr)}  \n {str(stdout)}",  f"{os.getcwd()}/{build_image_file_name}"


def register_container(image_file_path, gcc):
    try:
        # Register sif file path, created after successfully building the image
        container_id = gcc.register_container(image_file_path, "singularity")

        return container_id

    except Exception as ex:
        raise RegisterImageException(ex)


def build_image(gc_executor,
                image_file_name,
                base_image_type,
                base_image,
                payload_url, pip_packages, conda_packages, apt_packages):
    """Calls Globus compute executor which Builds apptainer/singularity image on Delta using funcX, return path of the image and logs

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
    try:
        fut = gc_executor.submit(funcx_build_image,
                                 image_file_name,
                                 base_image_type,
                                 base_image,
                                 payload_url,
                                 pip_packages,
                                 conda_packages,
                                 apt_packages)

        # Wait till future is completed poll every 30 sec
        while not fut.done():
            sleep(30)

        logs, image_file_path = fut.result()
        return image_file_path
    except Exception as ex:
        raise ImageBuilderException(ex)


def build_and_register_container(endpoint_id,
                                 image_file_name,
                                 base_image_type,
                                 base_image,
                                 payload_url=None,
                                 pip_packages=None,
                                 conda_packages=None,
                                 apt_packages=None):
    """Calls Globus compute executor and client which Builds apptainer/singularity image on Delta using funcX, and
    registers the image returning the container id

        :param endpoint_id:
        :param apt_packages:
        :param conda_packages:
        :param pip_packages:
        :param payload_url:
        :param base_image:
        :param image_file_name:
        :param base_image_type:
        :return: container_id """
    gc_executor = Executor(endpoint_id=endpoint_id)
    gcc = Client()

    image_file_path = build_image(gc_executor,
                                  image_file_name,
                                  base_image_type,
                                  base_image,
                                  payload_url,
                                  pip_packages,
                                  conda_packages,
                                  apt_packages)

    return register_container(image_file_path, gcc)


# if __name__ == '__main__':
#     container_id = build_and_register_container("01e21ddf-6eb4-41db-8e1d-2bcfe0c8314f",
#                                                 "test-image", "docker", "python:3.8")
#
#     print("Container id ", container_id)
