########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\router.py total lines 32 
########################################################################

from __future__ import annotations
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import random
import os

class StrategyRouter:
    def __init__(self, strategies: List[str], seed: Optional[int] = None):
        self.strategies = strategies or ["default"]
        self._rng = random.Random(seed or int(os.getenv("FLOWORK_ROUTER_SEED", "0") or "0"))

    def pick(self, context: Dict[str, Any]) -> str:
        if "force_strategy" in context:
            return context["force_strategy"]
        return self._rng.choice(self.strategies)

class BaseRouter(ABC):
    """
    Base class for all App Routers in Flowork Ecosystem.
    """
    def __init__(self, kernel):
        self.kernel = kernel

    @abstractmethod
    def get_routes(self):
        pass
