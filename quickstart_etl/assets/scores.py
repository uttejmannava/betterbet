import requests
import json
import os

from . import constants
from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, EnvVar, asset