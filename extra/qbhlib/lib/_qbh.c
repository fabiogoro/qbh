#include <Python.h>
#include <numpy/arrayobject.h>
#include "qbh.h"

static PyObject* _dtw(PyObject* self, PyObject *args)
{
  PyObject *q_obj, *x_obj;

  /* Parse the input tuple */
  if (!PyArg_ParseTuple(args, "OO", &q_obj, &x_obj))
    return NULL;

  /* Interpret the input objects as numpy arrays. */
  PyObject *q_array = PyArray_FROM_OTF(q_obj, NPY_DOUBLE, NPY_IN_ARRAY);
  PyObject *x_array = PyArray_FROM_OTF(x_obj, NPY_DOUBLE, NPY_IN_ARRAY);

  /* If that didn't work, throw an exception. */
  if (q_array == NULL || x_array == NULL) {
    Py_XDECREF(q_array);
    Py_XDECREF(x_array);
    return NULL;
  }

  /* How many data points are there? */
  int N = (int)PyArray_DIM(q_array, 0);
  int M = (int)PyArray_DIM(x_array, 0);

  /* Get pointers to the data as C-types. */
  double *q    = (double*)PyArray_DATA(q_array);
  double *x    = (double*)PyArray_DATA(x_array);

  /* Call the external C function to compute the dtw score. */
  double value = dtw(x, q, M, N);

  /* Clean up. */
  Py_DECREF(q_array);
  Py_DECREF(x_array);

  /* Build the output tuple */
  PyObject *ret = Py_BuildValue("d", value);
  return ret;
}

static PyObject* _smbgt(PyObject* self, PyObject *args)
{
  PyObject *q_obj, *x_obj;
  double gamma, delta, zeta, eta;
  int alpha, beta, dimension, debug;

  dimension = 2;
  /* Parse the input tuple */
  if (!PyArg_ParseTuple(args, "OOiiddddi|i", &q_obj, &x_obj, &alpha, &beta, &gamma, &delta, &zeta, &eta, &debug, &dimension))
    return NULL;

  /* Interpret the input objects as numpy arrays. */
  PyObject *q_array = PyArray_FROM_OTF(q_obj, NPY_DOUBLE, NPY_IN_ARRAY);
  PyObject *x_array = PyArray_FROM_OTF(x_obj, NPY_DOUBLE, NPY_IN_ARRAY);

  /* If that didn't work, throw an exception. */
  if (q_array == NULL || x_array == NULL) {
    Py_XDECREF(q_array);
    Py_XDECREF(x_array);
    return NULL;
  }

  /* How many data points are there? */
  int N = (int)PyArray_DIM(q_array, 0);
  int M = (int)PyArray_DIM(x_array, 0);

  /* Get pointers to the data as C-types. */
  double *q    = (double*)PyArray_DATA(q_array);
  double *x    = (double*)PyArray_DATA(x_array);

  /* Call the external C function to compute the smbgt score. */
  double value = smbgt(q, x, N/dimension, M/dimension, alpha, beta, gamma, delta, zeta, eta, dimension, debug);

  /* Clean up. */
  Py_DECREF(q_array);
  Py_DECREF(x_array);

  /* Build the output tuple */
  PyObject *ret = Py_BuildValue("d", value);
  return ret;
}

static char smbgt_docs[] =
"smbgt( ): Compute SMBGT score of two sequences.\n";
static char dtw_docs[] =
"dtw( ): Compute DTW score of two sequences.\n";

static PyMethodDef qbh_funcs[] = {
  {"smbgt", (PyCFunction)_smbgt, METH_VARARGS, smbgt_docs},
  {"dtw", (PyCFunction)_dtw, METH_VARARGS, dtw_docs},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cModPyDem =
{
    PyModuleDef_HEAD_INIT,
    "qbhlib", /* name of module */
    "Functions for computing qbh scores",          /* module documentation, may be NULL */
    -1,          /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    qbh_funcs
};

PyMODINIT_FUNC PyInit_qbhlib(void)
{
  import_array();
  return PyModule_Create(&cModPyDem);
}

void initqbhlib(void)
{
}
