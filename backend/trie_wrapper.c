#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "trie_engine.h"

// Initialize the trie
static PyObject* init_trie_wrapper(PyObject* self, PyObject* args) {
    init_trie();
    Py_RETURN_NONE;
}

// Insert a rule into the trie
static PyObject* insert_rule_wrapper(PyObject* self, PyObject* args) {
    const char *rule;
    if (!PyArg_ParseTuple(args, "s", &rule)) {
        return NULL;
    }
    insert_rule(rule);
    Py_RETURN_NONE;
}

// Search for a rule in the trie
static PyObject* search_rule_wrapper(PyObject* self, PyObject* args) {
    const char *rule;
    if (!PyArg_ParseTuple(args, "s", &rule)) {
        return NULL;
    }
    int found = search_rule(rule);
    return PyLong_FromLong(found);
}

// Free the trie
static PyObject* free_trie_wrapper(PyObject* self, PyObject* args) {
    free_trie();
    Py_RETURN_NONE;
}

// Method definitions
static PyMethodDef TrieMethods[] = {
    {"init_trie", init_trie_wrapper, METH_NOARGS, "Initialize the trie."},
    {"insert_rule", insert_rule_wrapper, METH_VARARGS, "Insert a rule into the trie."},
    {"search_rule", search_rule_wrapper, METH_VARARGS, "Search for a rule in the trie."},
    {"free_trie", free_trie_wrapper, METH_NOARGS, "Free the trie."},
    {NULL, NULL, 0, NULL} // Sentinel
};

// Module definition
static struct PyModuleDef triemodule = {
    PyModuleDef_HEAD_INIT,
    "trie_wrapper",   /* name of module */
    "Python interface for C trie engine",
    -1,
    TrieMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_trie_wrapper(void) {
    return PyModule_Create(&triemodule);
}
