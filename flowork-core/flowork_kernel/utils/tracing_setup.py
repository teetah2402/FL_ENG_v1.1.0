########################################################################
# WEBSITE https://flowork.cloud
# File NAME : C:\flowork-nano\flowork-core\flowork_kernel\utils\tracing_setup.py total lines 49 
########################################################################

import logging


class DummySpan:
    """
    A dummy span that mimics OpenTelemetry span for context management.
    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def set_attribute(self, key, value):
        pass

    def set_status(self, status):
        pass

    def record_exception(self, exception):
        pass

class DummyTracer:
    """
    A dummy tracer that returns dummy spans.
    """
    def start_as_current_span(self, name, *args, **kwargs):
        return DummySpan()

def setup_tracing(service_name="flowork-core"):
    """
    [LITE MODE STUB]
    Returns a dummy tracer provider.
    Does NOT initialize OpenTelemetry or Jaeger exporters.
    """
    return DummyTracer()

def get_trace_context_from_headers(headers):
    """
    [LITE MODE STUB]
    Returns None as distributed tracing is disabled.
    """
    return None
