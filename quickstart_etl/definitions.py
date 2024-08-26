from pathlib import Path
import requests
from requests import Response
from datetime import datetime, timedelta

from dagster import (
    Definitions,
    ScheduleDefinition,
    ConfigurableResource,
    EnvVar,
    define_asset_job,
    graph_asset,
    link_code_references_to_git,
    load_assets_from_package_module,
    load_assets_from_modules,
    op,
    with_source_code_references,
    build_last_update_freshness_checks,
    build_sensor_for_freshness_checks,
)
from dagster._core.definitions.metadata.source_code import AnchorBasedFilePathMapping

from .assets import odds
from .resources import *

# daily_refresh_schedule = ScheduleDefinition(
#     job=define_asset_job(name="all_assets_job"), cron_schedule="0 0 * * *"
# )

# @op
# def foo_op():
#     return 5


# @graph_asset
# def my_asset():
#     return foo_op()

# my_assets = link_code_references_to_git(
#     assets_defs=my_assets,
#     git_url="https://github.com/dagster-io/dagster/",
#     git_branch="master",
#     file_path_mapping=AnchorBasedFilePathMapping(
#         local_file_anchor=Path(__file__).parent,
#         file_anchor_path_in_repository="examples/quickstart_etl/quickstart_etl/",
#     ),
# )

my_assets = with_source_code_references(
    [
        *load_assets_from_modules([odds]),
    ]
)

raw_odds_data_freshness_check = build_last_update_freshness_checks(
    assets=[odds.raw_odds_data], lower_bound_delta=timedelta(minutes=2)
)


freshness_checks_sensor = build_sensor_for_freshness_checks(
    freshness_checks=raw_odds_data_freshness_check
)


defs = Definitions(
    assets=my_assets,
    resources={
        "odds_api": OddsBlazeAPIResource()
    },
    asset_checks=raw_odds_data_freshness_check,
    sensors=[freshness_checks_sensor],

    # schedules=[daily_refresh_schedule],
)
