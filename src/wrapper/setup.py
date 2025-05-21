from setuptools import find_packages, setup

package_name = 'wrapper'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    # install_requires=['setuptools'],
    install_requires=['setuptools', 'px4_msgs'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='bbt1203@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'wrapper_node = wrapper.wrapper_node:main'
        ],
    },
)
