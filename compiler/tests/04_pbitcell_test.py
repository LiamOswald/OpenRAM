#!/usr/bin/env python2.7
"""
Run regresion tests on a parameterized inverter
"""

import unittest
from testutils import header
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
import globals
import debug
import verify

OPTS = globals.OPTS

#@unittest.skip("SKIPPING 04_pbitcell_test")


class pbitcell_test(unittest.TestCase):

    def runTest(self):
        globals.init_openram("config_20_{0}".format(OPTS.tech_name))
        OPTS.check_lvsdrc = False

        import pbitcell
        import tech

        debug.info(2, "Test for pbitcell with 2 write ports and 2 read ports")
        tx = pbitcell.pbitcell(num_write=2,num_read=2)
        self.local_check(tx)

        OPTS.check_lvsdrc = True
        globals.end_openram()        

    def local_check(self, tx):
        #tempspice = OPTS.openram_temp + "temp.sp"
        tempgds = OPTS.openram_temp + "temp.gds"

        #tx.sp_write(tempspice)
        tx.gds_write(tempgds)

        self.assertFalse(verify.run_drc(tx.name, tempgds))
        #self.assertFalse(verify.run_lvs(tx.name, tempgds, tempspice))

        #os.remove(tempspice)
        os.remove(tempgds)

        # reset the static duplicate name checker for unit tests
        import design
        design.design.name_map=[]




# instantiate a copy of the class to actually run the test
if __name__ == "__main__":
    (OPTS, args) = globals.parse_args()
    del sys.argv[1:]
    header(__file__, OPTS.tech_name)
    unittest.main()
