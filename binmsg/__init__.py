import sys
if sys.version_info<(3,0,0):
    from binmsg import *
else:
    from binmsg.binmsg import *
