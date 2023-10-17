import unittest
from unittest.mock import Mock
from unittest.mock import MagicMock

from custom_image_builder.image_builder import build_image, register_container
from custom_image_builder.exception.RegisterImageException import RegisterImageException
from custom_image_builder.exception.ImageBuilderException import ImageBuilderException


class TestImageBuilder(unittest.TestCase):

    def test_register_container_raise_exception(self):
        gcc = Mock()
        gcc.register_container.side_effect =  Exception("Failed to register image, Globus Compute error")

        with self.assertRaises(RegisterImageException):
            register_container("container_file_path", gcc)

    def test_build_image_raise_exception(self):
        fut = Mock()
        fut.result.side_effect = Exception("Failed to build image, Globus Compute error")
        gc_executor = Mock()
        gc_executor.submit.return_value = fut

        with self.assertRaises(ImageBuilderException):
            build_image(gc_executor,
                        "test-image",
                        "docker",
                        "python:3.8",
                        payload_url=None,
                        pip_packages=["pandas"],
                        apt_packages=None,
                        conda_packages=None)

    def test_build_image(self):
        gc_executor = MagicMock()
        gc_executor.__enter__.return_value.submit.return_value.result.return_value = ("logs", "container_path")
        container_id = build_image(gc_executor,
                                   "test-image",
                                   "docker",
                                   "python:3.8",
                                   payload_url=None,
                                   pip_packages=["pandas"],
                                   apt_packages=None,
                                   conda_packages=None)


        print("The container id is:", container_id)

        self.assertEqual("container_path", container_id)

    def test_register_container(self):
        gcc = Mock()
        gcc.register_container.return_value = "container_id"
        container_id = register_container("container_path", gcc)

        print("The container id is:", container_id)

        self.assertEqual("container_id", container_id)
