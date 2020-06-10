from distutils.core import setup, Extension

loggerModule = Extension('Logger',
			 include_dirs = ['/usr/include'],
			 libraries = ['wiringPi'],
			 library_dirs = ['/usr/lib'],
			 sources = ['logger.c'])

setup(name = 'Logger', version = '1.0', ext_modules = [loggerModule])

# This code was derived from Python.h and python-dev tutorials.
# This code is only called by setup.sh, and is simply used to compile the file logger.c.
