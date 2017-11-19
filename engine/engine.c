
#include <Python.h>

/*
 * Implements an example function.
 */
PyDoc_STRVAR(engine_example_doc, "command(cmd)\
\
Example function");

extern char* command(const char*);

PyObject *engine_command(PyObject *self, PyObject *args, PyObject *kwargs) {
    /* Shared references that do not need Py_DECREF before returning. */
    const char* cmd = NULL;
	char* respond;
	PyObject* r;
    /* Parse positional and keyword arguments */
    static char* keywords[] = { "cmd", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s", keywords, &cmd)) {
        return NULL;
    }
	respond = command(cmd);
	r = PyUnicode_FromString(respond);
	free(respond);
	return r;
}

/*
 * List of functions to add to engine in exec_engine().
 */
static PyMethodDef engine_functions[] = {
    { "command", (PyCFunction)engine_command, METH_VARARGS | METH_KEYWORDS, engine_example_doc },
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
