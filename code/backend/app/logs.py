import logging

from app.core.settings import settings
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Tracer


def setup_logging(module) -> logging.Logger:
    """Setup logging and event handler.

    :param module: The module for which the logger is being set up.
    :type module: str
    :returns: The logger object to log activities.
    :rtype: logging.Logger
    """
    logger = logging.getLogger(module)
    logger.setLevel(settings.LOGGING_LEVEL)

    # Create stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(settings.LOGGING_FORMAT))
    logger.addHandler(stream_handler)
    return logger


def setup_tracer(module) -> Tracer:
    """Setup tracer and event handler.

    :param module: The module for which the tracer is being set up.
    :type module: str
    :returns: The tracer object to trace activities.
    :rtype: Tracer
    """
    tracer = trace.get_tracer(module)
    return tracer


def setup_opentelemetry():
    """Setup tracer for Open Telemetry.

    :returns: None
    :rtype: None
    """
    # Configure basic logging configuration
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(settings.LOGGING_FORMAT))
    logging.basicConfig(
        format=settings.LOGGING_FORMAT,
        handlers=[stream_handler],
        level=settings.LOGGING_LEVEL,
    )

    if settings.APPLICATIONINSIGHTS_AUTHENTICATION_STRING:
        credential = DefaultAzureCredential(
            managed_identity_client_id=settings.MANAGED_IDENTITY_CLIENT_ID,
        )
    else:
        credential = None

    # Create OTEL resource
    resource = Resource.create(
        attributes={
            "service.name": settings.WEBSITE_NAME,
            "service.namespace": settings.WEBSITE_NAME,
            "service.instance.id": settings.WEBSITE_INSTANCE_ID,
        }
    )

    # Configure azure monitor
    configure_azure_monitor(
        credential=credential,
        connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING,
        enable_live_metrics=True,
        enable_performance_counters=True,
        enable_trace_based_sampling_for_logs=False,
        instrumentation_options={
            "azure_sdk": {"enabled": True},
            "django": {"enabled": False},
            "fastapi": {"enabled": True},
            "flask": {"enabled": False},
            "psycopg2": {"enabled": False},
            "requests": {"enabled": False},
            "urllib": {"enabled": False},
            "urllib3": {"enabled": False},
        },
        storage_directory=os.path.join(settings.HOME_DIRECTORY, "azure_monitor"),
        resource=resource,
    )

    # Configure custom metrics
    system_metrics_config = {
        "system.memory.usage": ["used", "free", "cached"],
        "system.cpu.time": ["idle", "user", "system", "irq"],
        "system.network.io": ["transmit", "receive"],
        "process.runtime.memory": ["rss", "vms"],
        "process.runtime.cpu.time": ["user", "system"],
    }

    # Add additional instrumentations and configurations
    OpenAIAgentsInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
    HTTPXClientInstrumentor().instrument()
    SystemMetricsInstrumentor(config=system_metrics_config).instrument()
