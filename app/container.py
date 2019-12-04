"""Example of dependency injection in Python."""

import main, appconfig, logging
from dependency_injector import containers, providers
from masternode.blockchain import core_node
from masternode import mnsync
from persistence.repository import redis
from jobs import discovery


class IocContainer(containers.DeclarativeContainer):
    """Application IoC container."""
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name='VelesMasternode')


    # Core app components
    app_config = providers.Singleton(
        appconfig.ApplicationConfig,
        filename=config.config
    )

    # Gateways, repos
    redis_gateway = providers.Singleton(
        redis.RedisGateway,
        config=app_config
    )
    repos = {
        'MasternodeRepository': providers.Singleton(
            redis.MasternodeRepository,
            redis_gateway=redis_gateway
        )
    }

    # Services
    services = {
        'CoreNodeService': providers.Factory(
            core_node.CoreNodeService,
            config=app_config,
            logger=logger
        )
    }
    services['MasternodeSyncService'] = providers.Factory(
        mnsync.MasternodeSyncService,
        masternode_repo=repos['MasternodeRepository'],
        core_node_service=services['CoreNodeService'],
        logger=logger
    )

    # Jobs
    jobs = {
        'ServiceDiscovery': providers.Factory(
            discovery.ServiceDiscovery,
            mnsync_service=services['MasternodeSyncService'],
            logger=logger,
            config=app_config
        )
    }

    # Main
    run_job = providers.Callable(
        main.run_job,
        jobs,
    )
