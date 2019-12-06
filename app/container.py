"""Example of dependency injection in Python."""

import main, appconfig, logging
from dependency_injector import containers, providers
from blockchain import core_node
from masternode import mnsync, signing
from jobs import discovery, webserver
from controllers import status
from dapps import registry


class IocContainer(containers.DeclarativeContainer):
    """Application IoC container."""
    db_type = 'mem'
    config = providers.Configuration('config')
    logger = providers.Singleton(logging.Logger, name='VelesMasternode')


    # Core app components
    app_config = providers.Singleton(
        appconfig.ApplicationConfig,
        filename=config.config
    )

    # Gateways, repos
    if db_type == 'redis':
        from persistence.repository import redis

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
    else:
        from persistence.repository import mem

        repos = {
            'MasternodeRepository': providers.Singleton(
                mem.MasternodeRepository
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
    services.update({
        'MasternodeSyncService': providers.Factory(
            mnsync.MasternodeSyncService,
            masternode_repo=repos['MasternodeRepository'],
            core_node_service=services['CoreNodeService'],
            logger=logger
        )
    })
    services.update({
        'MasternodeSigningService': providers.Factory(
            signing.MasternodeSigningService,
            core_node_service=services['CoreNodeService'],
            mnsync_service=services['MasternodeSyncService'],
            config=app_config,
            logger=logger
        )
    })

    # Dapps
    dapp_registry = providers.Factory(
        registry.dAppRegistry,
        config=app_config,
        logger=logger
    )

    # Controllers
    controllers = {
        'StatusController': providers.Factory(
            status.StatusController,
            config=app_config,
            logger=logger,
            signing_service=services['MasternodeSigningService'],
            core_node=services['CoreNodeService'],
            dapp_registry=dapp_registry
        )
    }

    # Jobs
    jobs = {
        'ServiceDiscovery': providers.Factory(
            discovery.ServiceDiscovery,
            mnsync_service=services['MasternodeSyncService'],
            config=app_config,
            logger=logger
        ),
        'WebServer': providers.Factory(
            webserver.WebServer,
            controllers=controllers,
            config=app_config,
            logger=logger
        ),
    }

    # Main
    run_job = providers.Callable(
        main.run_job,
        jobs,
    )

