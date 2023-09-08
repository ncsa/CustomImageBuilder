from globus_compute_sdk import Client

gcc = Client()

def build_image(container_spec):
    """Builds apptainer/singulairty image on Delta using funcX, return path of the image and logs


    :param container_spec:
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
        "container_type": container_spec.get("container_type", None),
        "base_image": container_spec.get("base_image", None),
        "payload_url": container_spec.get("payload_url", None),
        "pip": container_spec.get("pip", None),
        "apt": container_spec.get("apt", None),
        "conda": container_spec.get("conda", None)
    })

    build_image_file_name = container_spec["image_file_name"]
    open(f"{build_image_file_name}.def", "w").write(build_file)

    process = subprocess.Popen(
        f"apptainer build --force {build_image_file_name}.sif {build_image_file_name}.def",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )

    stdout, stderr = process.communicate()

    return f"Output logs are as follows: \n {str(stderr)}  \n {str(stdout)}  {os.getcwd() } / {build_image_file_name}"


def main():
    func_uuid = gcc.register_function(build_image, public=True)
    print("The function uuid", func_uuid)


if __name__ == '__main__':
    main()
