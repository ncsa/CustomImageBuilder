from custom_image_builder import build_and_register_container
from globus_compute_sdk import Client, Executor
from globus_compute_sdk.serialize import DillCodeSource


def transform():
    import pandas as pd
    data = {'Column1': [1, 2, 3],
            'Column2': [4, 5, 6]}

    df = pd.DataFrame(data)

    return "Successfully created df"


def main():
    image_builder_endpoint = "bc106b18-c8b2-45a3-aaf0-75eebc2bef80"
    gcc_client = Client(code_serialization_strategy=DillCodeSource())

    container_id = build_and_register_container(gcc_client=gcc_client,
                                                endpoint_id=image_builder_endpoint,
                                                image_file_name="my-pandas-image",
                                                base_image_type="docker",
                                                base_image="python:3.8",
                                                pip_packages=["pandas"])

    print("The container id is", container_id)

    with Executor(endpoint_id=image_builder_endpoint,
                  container_id=container_id) as ex:
        fut = ex.submit(transform)

    print(fut.result())


if __name__ == '__main__':
    main()
