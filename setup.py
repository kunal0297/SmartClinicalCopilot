from setuptools import setup, Extension

module = Extension(
    "trie_wrapper",
    sources=[
        "backend/trie_engine.c",
        "backend/trie_wrapper.c"
    ],
    extra_compile_args=["-O3"],
    language="c"
)

setup(
    name="trie_wrapper",
    version="1.0",
    description="Python C extension wrapper for trie engine",
    ext_modules=[module],
)
