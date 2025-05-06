from setuptools import setup, Extension

trie_module = Extension(
    'trie_wrapper',
    sources=['trie_engine.c', 'trie_wrapper.c'],
    include_dirs=['.'],
    define_macros=[('PY_SSIZE_T_CLEAN', None)]
)

setup(
    name='trie_wrapper',
    version='1.0',
    description='Trie data structure wrapper for Python',
    ext_modules=[trie_module],
) 