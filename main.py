import logging
import src.eurocore as eurocore
import src.ns as ns
import src.utils as utils
import sys

from src.config import Config

logger = logging.getLogger("main")


def main():
    if len(sys.argv) >= 2:
        config = Config.from_yml(sys.argv[1])
    else:
        config = Config.from_yml()
    logger.info("running")

    pop = ns.get_population(config.user, config.region)

    try:
        old_pop = utils.get_old_pop(config.population_cache)
        if not old_pop:
            logger.info(
                "file: %s does not exist, assuming first time run",
                config.population_cache,
            )

            return

        new_pop = [nation for nation in pop if nation not in old_pop]

        logger.info("new nations: %d", len(new_pop))
        if len(new_pop) == 0:
            return

        token = eurocore.login(
            config.eurocore.url, config.eurocore.user, config.eurocore.password
        )

        eurocore.post(
            config.eurocore.url,
            token,
            config.rmbpost.template,
            config.rmbpost.author,
            config.region,
            new_pop,
        )
    except:
        logger.exception("unable to publish rmbpost")
    finally:
        utils.write_old_pop(config.population_cache, pop)


if __name__ == "__main__":
    main()
