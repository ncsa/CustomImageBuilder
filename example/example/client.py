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


if __name__ == '__main__':
    main()
