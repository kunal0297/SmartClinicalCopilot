#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Declare trie engine functions and struct from trie_engine.c
typedef struct TrieNode TrieNode;

TrieNode* create_node();
void insert(TrieNode *root, const char *rule);
int search(TrieNode *root, const char *rule);
void free_trie(TrieNode *root);

static TrieNode *trie_root = NULL;

// Initialize the trie
static PyObject* init_trie(PyObject* self, PyObject* args) {
    if(trie_root != NULL) {
        free_trie(trie_root);
    }
    trie_root = create_node();
    Py_RETURN_NONE;
}

// Insert a rule into the trie
static PyObject* insert_rule(PyObject* self, PyObject* args) {
    const char *rule;
    if (!PyArg_ParseTuple(args, "s", &rule)) {
        return NULL;
    }
    if (trie_root == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Trie not initialized. Call init_trie first.");
        return NULL;
    }
    insert(trie_root, rule);
    Py_RETURN_NONE;
}

// Search for a rule in the trie
static PyObject* search_rule(PyObject* self, PyObject* args) {
    const char *rule;
    if (!PyArg_ParseTuple(args, "s", &rule)) {
        return NULL;
    }
    if (trie_root == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Trie not initialized. Call init_trie first.");
        return NULL;
    }
    int found = search(trie_root, rule);
    return PyLong_FromLong(found);
}

// Free the trie
static PyObject* free_trie_wrapper(PyObject* self, PyObject* args) {
    if (trie_root != NULL) {
        free_trie(trie_root);
        trie_root = NULL;
    }
    Py_RETURN_NONE;
}

// Method definitions
static PyMethodDef TrieMethods[] = {
    {"init_trie", init_trie, METH_NOARGS, "Initialize the trie."},
    {"insert_rule", insert_rule, METH_VARARGS, "Insert a rule into the trie."},
    {"search_rule", search_rule, METH_VARARGS, "Search for a rule in the trie."},
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
