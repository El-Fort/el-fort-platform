from setuptools import setup, find_packages
setup(name='efn-subscriptions', version='1.0.0',
      description='EFN Biometric Subscription Payments SDK',
      packages=find_packages(),
      install_requires=['requests>=2.28'],
      python_requires='>=3.8')
