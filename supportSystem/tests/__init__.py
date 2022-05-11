import unittest

def suite():
    return unittest.TestLoader().discover("supportSystem.tests", pattern="test_*.py")