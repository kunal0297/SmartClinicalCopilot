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
    description="High-performance C-based Trie for clinical rule matching",
    ext_modules=[module],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
