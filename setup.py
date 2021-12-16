# #!/usr/bin/env python

# import os
# import sys

# import setuptools

# setup_dir = os.path.dirname(os.path.abspath(__file__))
# release_filename = os.path.join(setup_dir, "src", "tmc", "common", "release.py")
# exec(open(release_filename).read())

# # prevent unnecessary installation of pytest-runner
# needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
# pytest_runner = ["pytest-runner"] if needs_pytest else []

# setuptools.setup(
#     name=name,
#     description=description,
#     version=version,
#     author=author,
#     author_email=author_email,
#     license=license,
#     packages=setuptools.find_namespace_packages(where="src", include=["tmc.*"]),
#     package_dir={"": "src"},
#     include_package_data=True,
#     url="https://www.skatelescope.org/",
#     classifiers=[
#         "Development Status :: 3 - Alpha",
#         "Intended Audience :: Developers",
#         "License :: Other/Proprietary License",
#         "Operating System :: OS Independent",
#         "Programming Language :: Python",
#         "Topic :: Software Development :: Libraries :: Python Modules",
#         "Topic :: Scientific/Engineering :: Astronomy",
#     ],
#     platforms=["OS Independent"],
#     setup_requires=[] + pytest_runner,
#     install_requires=["pytango==9.3.3", "mock", "future", "transitions"],
#     tests_require=["pytest", "coverage", "pytest-json-report", "pytest-forked"],
#     entry_points={
#         "console_scripts": [
#             "TangoClient=tmc.common.tango_client:main",
#             "TangoGroupClient=tmc.common.tango_group_client:main",
#             "TangoServerHelper=tmc.common.tango_server_helper:main",
#         ]
#     },
#     keywords="tmc common ska",
#     zip_safe=False,
# )
