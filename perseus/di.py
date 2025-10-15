from dependency_injector import containers, providers
from perseus.cli.perseus_service import PerseusService


class Container(containers.DeclarativeContainer):
    """Lightweight DI container for Perseus.

    The container exposes a `config` provider (configured at runtime) and a
    `perseus_service` factory wiring the `PerseusService` to that configuration. This
    keeps bootstrapping contained and test-friendly.
    """

    config = providers.Configuration()

    # Provide a factory for the CLI so callers can request a CLI wired with
    # the container-configured values.
    perseus_service = providers.Factory(PerseusService, config=config)
