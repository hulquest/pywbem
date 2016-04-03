#!/usr/bin/env python
#

from __future__ import print_function
import sys
import os
from time import time
from zipfile import ZipFile
from tempfile import TemporaryFile
import unittest
import six

from pywbem.cim_operations import CIMError
from pywbem.mof_compiler import MOFCompiler, MOFWBEMConnection, MOFParseError
from pywbem.cim_constants import *

import test_mof_compiler

## Constants
NAME_SPACE = 'root/test'

SCRIPT_DIR = os.path.dirname(__file__)
SCHEMA_DIR = os.path.join(SCRIPT_DIR, 'schema')
CIM_SCHEMA_MOF = 'cim_schema_2.45.0.mof'

TMP_FILE = 'test_tomofoutput.mof'

class DummyCIMOM(object):
    """
        Dummy PyWBEM CIMOM definition to provide context for compiling
        MOF and placing resulting classes, instances, and qualifiers in
        a set of python dictionaries defined by this class.

        This corresponds to the wbemcli class in pywbem but only allows
        the methods for qualifier Declaration, Class, and Intance
        creation.

        The result is either compile errors or the results in:
           - qualifierDecls dictionary for qualifiers
           - classes dictionary for classes:
           - instances dictionary for instances.
    """

    default_namespace = NAME_SPACE
    namespace = NAME_SPACE

    def __init__(self):
        self.qualifierDecls = {}
        self.classes = {}
        self.instances = {}

    def SetQualifier(self, qd, namespace=None, **params):
        self.qualifierDecls[qd.name] = qd

    def CreateClass(self, cl, namespace=None, **params):
        self.classes[cl.classname] = cl

    def CreateInstance(self, inst, namespace=None, **params):
        self.instances[inst.name] = inst

def setUpModule():
    if not os.path.isdir(test_mof_compiler, SCHEMA_DIR):
        test_mof_compiler.setUpModule()


class TestCompileMof(unittest.TestCase):
    """Compile the schema defined in schemas directory into memory.
       Then write the the resulting objects out as MOF to a
       temporary file and recompile again.
       """

    cimom = DummyCIMOM()

    SCHEMA_DIR = test_mof_compiler.SCHEMA_DIR
    CIM_SCHEMA_MOF = test_mof_compiler.CIM_SCHEMA_MOF

    verbose = True
    mofc = MOFCompiler(handle=cimom,
                       search_paths=[SCHEMA_DIR], verbose=False)

    mofc.compile_file(os.path.join(SCHEMA_DIR, CIM_SCHEMA_MOF),
                      NAME_SPACE)

    f1 = open(TMP_FILE, 'w')

    if len(cimom.qualifierDecls) != 0 and verbose:
        for name in sorted(cimom.qualifierDecls):
            qd = cimom.qualifierDecls[name]
            print('{}'.format(qd.tomof()), file=f1)

    if len(cimom.classes) != 0 and verbose:
        for name in sorted(cimom.classes):
            cl = cimom.classes[name]
            print('{}'.format(cl.tomof()), file=f1)

    # reopen the test output file and compile
    mofc2 = MOFCompiler(handle=cimom, verbose=False)
    mofc.compile_file(TMP_FILE, NAME_SPACE)

    # test for equal same number of elements in second compile
    self.assertEqual(len(mofc.classes), len(mofc2.classes))
    self.assertEqual(len(mofc.instances), len(mofc2.instances))
    self.assertEqual(len(mofc.qualifierDecls), len(mofc2.qualifierDecls))


    # Compare the recompiled mof with the original mof
    # TODO write the compare functions


    os.remove(TMP_FILE)

if __name__ == '__main__':
    unittest.main()
