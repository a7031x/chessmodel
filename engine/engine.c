
#include <Python.h>

/*
 * Implements an example function.
 */
PyDoc_STRVAR(engine_example_doc, "example(obj, cmd)\
\
Example function");

extern char* command(char*);

PyObject *engine_example(PyObject *self, PyObject *args, PyObject *kwargs) {
    /* Shared references that do not need Py_DECREF before returning. */
    PyObject *obj = NULL;
    const char* cmd = NULL;

    /* Parse positional and keyword arguments */
    static char* keywords[] = { "obj", "cmd", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Os", keywords, &obj, &cmd)) {
        return NULL;
    }

	return PyUnicode_FromString(command(cmd));
}

/*
 * List of functions to add to engine in exec_engine().
 */
static PyMethodDef engine_functions[] = {
    { "example", (PyCFunction)engine_example, METH_VARARGS | METH_KEYWORDS, engine_example_doc },
    { NULL, NULL, 0, NULL } /* marks end of array */
};

/*
 * Initialize engine. May be called multiple times, so avoid
 * using static state.
 */
int exec_engine(PyObject *module) {
    PyModule_AddFunctions(module, engine_functions);

    PyModule_AddStringConstant(module, "__author__", "easton");
    PyModule_AddStringConstant(module, "__version__", "1.0.0");
    PyModule_AddIntConstant(module, "year", 2017);

    return 0; /* success */
}

/*
 * Documentation for engine.
 */
PyDoc_STRVAR(engine_doc, "The engine module");


static PyModuleDef_Slot engine_slots[] = {
    { Py_mod_exec, exec_engine },
    { 0, NULL }
};

static PyModuleDef engine_def = {
    PyModuleDef_HEAD_INIT,
    "engine",
    engine_doc,
    0,              /* m_size */
    NULL,           /* m_methods */
    engine_slots,
    NULL,           /* m_traverse */
    NULL,           /* m_clear */
    NULL,           /* m_free */
};

PyMODINIT_FUNC PyInit_engine() {
    return PyModuleDef_Init(&engine_def);
}
