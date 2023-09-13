from custom_image_builder.image_builder import build_and_register_container


def main():
    container_id = build_and_register_container("01e21ddf-6eb4-41db-8e1d-2bcfe0c8314f",
                                                "my-test-image", "docker", "python:3.8")

    print("Container id ", container_id)


if __name__ == '__main__':
    main()
