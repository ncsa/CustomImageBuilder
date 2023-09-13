from globus_compute_sdk import Client, Executor
from time import sleep

gcc = Client()
IMAGE_BUILDER_ENDPOINT_ID = "01e21ddf-6eb4-41db-8e1d-2bcfe0c8314f"
IMAGE_BUILDER_FUNC_ID = "32ac0061-9d36-4260-9619-b91fd97b333c"


def main():
    # Define your container specs
    container_spec = {
        "image_file_name": "my-img",
        "container_type": "docker",
        "base_image": "python:3.8",
        "pip": ["pandas"]
    }

    # Build your image and get container path
    task_id = gcc.run(container_spec, endpoint_id=IMAGE_BUILDER_ENDPOINT_ID, function_id=IMAGE_BUILDER_FUNC_ID)

    while gcc.get_task(task_id).get('pending', False):
        # Waiting for task to complete
        sleep(2)

    logs, container_path = gcc.get_result(task_id)

    print("The debug logs", logs)
    print("The container path", container_path)

    # Register container path
    container_id = gcc.register_container(container_path, "singularity")
    print("Container Id", container_id)

    # Run your custom_function using custom_image

    #Execute sample function using custom_image
    # with Executor(endpoint_id="cf1ad80c-06b6-46ea-9eef-bc1f59d657ac", container_id="874e8336-d57f-4304-b86e-9870dee98130") as gce:
    #     def foo(data):
    #         import pandas as pd
    #         return pd.DataFrame(data)
    #
    #
    #     data = {
    #         'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    #         'Age': [25, 30, 35, 28, 22],
    #         'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami']
    #     }
    #     r = gce.submit(foo, data)
    #
    #     print(f"Foo is {r.result()}")


if __name__ == '__main__':
    main()
