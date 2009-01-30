"""
An example of how to use the pyfusion code for preprocessing of Mirnov data for clustering.

a file called 'pyfusion_local_settings.py' exists in the python path, with contents:
DEVICE='H1'

"""

import pyfusion

diag_name = 'mirnovbeans'
shot_number = 58048

# tweak above parameters according to command line args
execfile('process_cmd_line_args.py')

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

generate_flucstrucs(s, diag_name, 'test_flucstrucs', store_chronos=True)
