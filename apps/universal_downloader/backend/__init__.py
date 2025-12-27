########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\apps\universal_downloader\backend\__init__.py total lines 23 
########################################################################

import os
import sys

current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from .node import DownloaderNode
    from .service import DownloaderService
    from .router import AppRouter
except ImportError as e:
    from node import DownloaderNode
    from service import DownloaderService
    from router import AppRouter

__all__ = ["DownloaderNode", "DownloaderService", "AppRouter"]
