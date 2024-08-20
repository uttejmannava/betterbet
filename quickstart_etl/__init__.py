# from dagster import Definitions, ConfigurableResource, EnvVar, load_assets_from_modules
# import requests
# from requests import Response

# from .assets import odds, scores
# # from .jobs import trip_update_job, weekly_update_job, adhoc_request_job
# # from .schedules import trip_update_schedule, weekly_update_schedule
# # from .sensors import adhoc_request_sensor

# odds_assets = load_assets_from_modules([odds])
# scores_assets = load_assets_from_modules([scores])

# # odds_api_key_resource = EnvVar("THE_ODDS_API_KEY")
# class OddsAPIResource(ConfigurableResource):

#     def request(self, endpoint: str) -> Response:
#         return requests.get(
#             f"https://my-api.com/{endpoint}",
#             headers={"user-agent": "dagster"},
#         )

# defs = Definitions(
#     assets=odds_assets + scores_assets,
#     resources={
#         "odds_api_key": OddsAPIResource()
#     }
# )
