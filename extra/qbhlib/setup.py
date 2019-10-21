from distutils.core import setup, Extension
import numpy.distutils.misc_util
setup(name='qbhlib', version='1.0',  \
      ext_modules=[Extension('qbhlib', ['lib/_qbh.c', 'lib/qbh.c'])], 
      include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs(),
      )
