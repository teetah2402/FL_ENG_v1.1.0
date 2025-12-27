########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\globals.py total lines 33 
########################################################################

KERNEL_INSTANCE = None

class GlobalsProxy:
    """
    Proxy class to maintain compatibility with Gateway-style routes
    that expect 'globals_instance'.
    """
    def __init__(self):
        self.kernel = None

globals_instance = GlobalsProxy()

def get_kernel():
    """
    Standard way to get Kernel in Core V2
    """
    return KERNEL_INSTANCE

def set_kernel(kernel):
    """
    Called by bootstrap.py during startup
    """
    global KERNEL_INSTANCE

    KERNEL_INSTANCE = kernel

    globals_instance.kernel = kernel
