# """Classes for setting up and executing a Soda Scan."""

# # from soda.scan import Scan
# import yaml
# from datetime import datetime
# import pytz
# import re
# import json
# # from common_utils.connectors.aws.s3 import S3Connector
# # from common_utils.storage.s3 import S3Storage
# import logging
# from typing import Optional
# # from loggers import get_stream_logger, common_logger


# class BaseSodaScan:
#     """Base Implementation of Soda Scans. Contains all functions necessary to run a Soda Check."""

#     def __init__(self, dq_config, *, engine_config=None,
#                  logger: Optional[logging.Logger] = None):
#         """
#         Initialize BaseSodaScan Class.

#         :param dq_config: Dict
#             Contains all necessary information to run a soda check including
#             engine, checks file path, checks to run, and parameters
#         :param engine_config: String
#             Yaml String to connect to the engine (Databricks/ Dremio)
#         :param logger : logging.Logger
#                 A custom logger
#         """
#         self.engine = dq_config['engine']
#         self.dq_config = dq_config
#         self.engine_config = engine_config
#         self.scan = Scan()
#         self.logger = logger if logger else get_stream_logger(__name__)

#     def _set_scan(self):
#         """Set up soda scan. Adds config and checks to the scan."""
#         self.scan.add_configuration_yaml_str(self.engine_config)
#         self._add_checks()

#     def _add_checks(self):
#         """Read the checks file and adds parameter data from dq_config before adding the dq checks to soda scan."""
#         checks = ''
#         with open(self.dq_config['dq_checks_path'], 'r') as file:
#             data = yaml.safe_load(file)
#         for key, value in data.items():
#             if key == self.dq_config['details']['check_name']:
#                 new_value = []
#                 if not self.dq_config['details'].get('parameters'):
#                     self.dq_config['details']['parameters'] = {'x': 'x'}
#                 for item in value:
#                     for param, param_value in self.dq_config['details']['parameters'].items():
#                         item = item.replace(param, param_value)
#                     new_value.append(item)
#                 check = yaml.dump({key: new_value})
#                 checks += check
#         self.logger.info(checks)
#         self.scan.add_sodacl_yaml_str(checks)

#     def run_dq(self):
#         """Set up scan, adds checks to config, executes scan, then processes and writes results."""
#         self.logger.debug(f'Initializing Scan')
#         self._set_scan()
#         self.logger.debug(f'Running DQ')
#         self.scan.execute()
#         self.scan.assert_no_error_logs()
#         results = self._process_results()
#         self._write_results(results)

#     def process_results(self):
#         """
#         Process soda check results and formats them in a list of dicts.

#         :return result_list: dict of soda results (one for each check)
#         """
#         result_list = list()
#         cur_time = str(datetime.now(tz=pytz.timezone('America/Chicago')))
#         for check in self.scan.get_scan_results()['checks']:
#             for metric_object in self.scan.get_scan_results()['metrics']:
#                 if metric_object['identity'] == check['metrics'][0]:
#                     datasource = re.search('checks for (.*)\\:', check['definition']).group(1)
#                     result_dict = {
#                         'file_path': self.dq_config.get("details").get("spark_dataset", {}).get(datasource, datasource),
#                         'datasource': datasource,
#                         'table': datasource,
#                         'column': check['column'],
#                         'check_name': metric_object['metricName'],
#                         'check_definition': check['name'],
#                         'check_type': check['type'],
#                         'result': check['outcome'],
#                         'check_value': metric_object['value'],
#                         'check_engine': 'dremio',
#                         'execution_time': cur_time,
#                         'execution_uuid': self.dq_config['execution_uuid']
#                     }
#                     result_list.append(result_dict)
#         self.logger.info(self.scan.get_logs_text())
#         return result_list

#     def write_results(self, results):
#         """
#         Write soda check results to s3 bucket.

#         :param results: list of results generated via process_results()
#         """
#         result_bucket = self.dq_config.get('result_bucket', None)
#         result_path = self.dq_config.get('result_path_with_timestamp', None)
#         self.logger.info(f'Result Bucket: {result_bucket}')
#         self.logger.info(f'Result Path: {result_path}')
#         if result_bucket and result_path:
#             storage_connector = S3Connector()
#             storage = S3Storage(connector=storage_connector, bucket=result_bucket)
#             try:
#                 old_results = json.loads(storage.read(result_path))
#                 results.extend(old_results)
#             except storage._client.exceptions.NoSuchKey:
#                 results = results
#             data = json.dumps(results)
#             storage.write(key_objs=[(result_path, data)])
#             storage_connector.disconnect()


# class SparkSodaScan(BaseSodaScan):
#     """
#     Implementation of Spark Soda Scan that inherits from BaseSodaScan.

#     Overrides/adds functions necessary to run a Soda Check in Spark.
#     """

#     def __init__(self, dq_config, *, engine_config=None,
#                  logger: Optional[logging.Logger] = None):
#         """
#         Initialize SparkSodaScan Class.

#         :param dq_config: Dict
#             Contains all necessary information to run a soda check including
#             engine, checks file path, checks to run, and parameters
#         :param engine_config: String
#             None for Spark Soda Scan
#         :param logger : logging.Logger
#                 A custom logger
#         """
#         super().__init__(dq_config, engine_config=engine_config,
#                          logger=logger)
#         self.scan.set_data_source_name('spark_df')
#         self.logger.info(f'Initialized Spark Scan')

#     def _read_spark_files(self):
#         """
#         Read files into memory and creates temp views of them so that Soda can leverage Spark SQL to run checks.

#         Uses the spark_datasets key from dq_config to convert each file into
#         a temp table of the name of the key.
#         """
#         from pyspark.sql import functions as F
#         spark = spark  # noqa
#         for key, value in self.dq_config['details']['spark_datasets']:
#             spark_df = spark.read.parquet(f"s3://{value}")
#             spark_df.createOrReplaceTempView(key)
#             if 'csv' in value:
#                 spark_df = spark.read.option("delimiter", ",").option("header", "true").csv(f"s3://{value}")
#                 spark_df = spark_df.select(
#                     [F.col(col).alias(re.sub("[^0-9a-zA-Z$]+", "_", col)) for col in spark_df.columns])
#                 print('READ CSV')
#             else:
#                 spark_df = spark.read.parquet(f"s3://{value}")
#         spark_df.createOrReplaceTempView(key)

#     def _set_scan(self):
#         self.scan.add_configuration_yaml_str(self.engine_config)
#         self._add_checks()
#         self._read_spark_files()


# class DremioSodaScan(BaseSodaScan):
#     """
#     Implementation of Dremio Soda Scan that inherits from BaseSodaScan.

#     Overrides/adds functions necessary to run a Soda Check in Dremio.
#     """

#     def __init__(self, dq_config, *, engine_config=None,
#                  logger: Optional[logging.Logger] = None):
#         """
#         Initialize SparkSodaScan Class.

#         :param dq_config: Dict
#             Contains all necessary information to run a soda check including
#             engine, checks file path, checks to run, and parameters
#         :param engine_config: String
#             Yaml String to connect to the Dremio engine
#         :param logger : logging.Logger
#                 A custom logger
#         """
#         super().__init__(dq_config, engine_config=engine_config,
#                          logger=logger)
#         self.scan.set_data_source_name('dremio_datasource')
#         self.logger.info(f'Initialized Dremio Scan')


# class DatabricksSodaScan(BaseSodaScan):
#     """
#     Implementation of Databricks Soda Scan that inherits from BaseSodaScan.

#     Overrides/adds functions necessary to run a Soda Check in Databricks.
#     """

#     def __init__(self, dq_config, *, engine_config=None,
#                  logger: Optional[logging.Logger] = None):
#         """
#         Initialize DatabricksSodaScan Class.

#         :param dq_config: Dict
#             Contains all necessary information to run a soda check including
#             engine, checks file path, checks to run, and parameters
#         :param engine_config: String
#             Yaml String to connect to the Databricks engine
#         :param logger : logging.Logger
#                 A custom logger
#         """
#         super().__init__(dq_config, engine_config=engine_config,
#                          logger=logger)
#         self.scan.set_data_source_name('databricks_datasource')
#         self.logger.info(f'Initialized Databricks Scan')


# """Class for getting config and executing a Soda Scan and checking results."""

# import yaml
# from datetime import datetime, time
# import hashlib
# import json
# import os
# # from common_utils.data_quality.soda_scan import DremioSodaScan, DatabricksSodaScan
# # from common_utils.connectors.aws.s3 import S3Connector
# # from common_utils.storage.s3 import S3Storage
# # from common_utils.storage.secrets.vault import VaultStorage
# # from common_utils.connectors.secrets.vault import VaultConnector
# import logging
# from typing import Optional
# # from loggers import get_stream_logger, common_logger


# # from common_utils.notifications import alation, slack, sentry #need to be built - add tickets


# class BaseSodaRunner:
#     """Base Implementation of Soda Runner. Contains all functions \
#     necessary to fetch config, execute a check, check failures, and send notifications and alerts."""

#     def __init__(self, dq_config, logger: Optional[logging.Logger] = None):
#         """
#         Initialize BaseSodaRunner Class.

#         :param dq_config: Dict
#             Contains all necessary information to run a soda check including
#             engine, alation schema and table, result bucket and path,
#             checks file path, checks to run, parameters, cluster_id
#         :param logger : logging.Logger
#                 A custom logger
#         """
#         self.dq_config = dq_config
#         self._validate_config()
#         if self.dq_config.get('result_path'):
#             upload_time = str(datetime.now()).replace('-', '').replace(' ', '_').replace(':', '').split('.')[0]
#             self.dq_config['result_path_with_timestamp'] = f"{self.dq_config['result_path']}_{upload_time}.json"
#         self.dq_config['execution_uuid'] = hashlib.sha1((str(time()) + str(dq_config)).encode('utf-8'))

#     def _validate_config(self):
#         required_keys = ["dq_checks_path", "engine", "details"]
#         if all(key in self.dq_config.keys() for key in required_keys) is False:
#             raise ValueError('Keys are missing in dq_config')
#         if not self.dq_config["details"][0].get("check_name"):
#             raise ValueError('Keys are missing in dq_config["details"]')

#     @staticmethod
#     def _get_dremio_config():
#         """
#         Get Dremio Config from Vault.

#         :return dremio_config: String
#             Yaml string of dremio config
#         """
#         env = os.environ['ENVIRONMENT']
#         vault_secret_path = f"user/devops/dremio/sa_{env}_user" if env == 'prod' else "user/devops/dremio/sa_user"
#         vault_connector = VaultConnector(run_mode='iam', url='https://vault.shared.partner01.data.avant.com')
#         vault_connector.connect()
#         vault_storage = VaultStorage(vault_connector)
#         vault_data = vault_storage.read(vault_secret_path)['data']['data']
#         vault_connector.disconnect()
#         dremio_host = f"dremio-prod.services.global.avant.com" if env == 'prod' else "dremio-nonprod.services.global" \
#                                                                                      ".avant.com"
#         dremio_config = {
#             'data_source dremio_datasource': {'type': 'dremio', 'host': dremio_host,
#                                               'port': "32010",
#                                               'username': vault_data['USERNAME'],
#                                               'password': vault_data['PASSWORD'],
#                                               'driver': '/opt/arrow-flight-sql-odbc-driver/lib64/libarrow-odbc.so.0.9'
#                                                         '.1.168',
#                                               'use_encryption': 'true'}}
#         dremio_config = yaml.dump(dremio_config)
#         return dremio_config

#     @staticmethod
#     def _get_databricks_config():
#         """
#         Get Databricks Config from Vault.

#         :return databricks_config: String
#             Yaml string of dremio config
#         """
#         raise NotImplementedError('Databricks Config Has Not Been Implemented Yet')
#         vault_secret_path = 'databricks_path'
#         vault_connector = VaultConnector(run_mode='iam', url='https://vault.shared.partner01.data.avant.com')
#         vault_connector.connect()
#         vault_storage = VaultStorage(vault_connector)
#         vault_data = vault_storage.read(vault_secret_path)['data']['data']
#         vault_connector.disconnect()
#         databricks_host = 'databricks_host'
#         databricks_config = {
#             'data_source databricks': {'type': 'databricks', 'host': databricks_host,
#                                        'username': vault_data['USERNAME'],
#                                        'password': vault_data['PASSWORD']}}
#         databricks_config = yaml.dump(databricks_config)
#         return databricks_config

#     def _get_engine_config(self):
#         """
#         Get Engine Config for Dremio/Databricks.

#         Check the engine in dq_config and calls the respective method
#         to get config
#         :return config: String
#             Yaml string of dremio/databricks config.
#         """
#         if self.dq_config['engine'] == 'dremio':
#             config = self._get_dremio_config()
#             self.logger.info(f"Running Soda on {self.dq_config['engine']}")
#         elif self.dq_config['engine'] == 'databricks':
#             config = self._get_databricks_config()
#             self.logger.info(f"Running Soda on {self.dq_config['engine']}")
#         elif self.dq_config['engine'] == 'spark':
#             config = None
#             self.logger.info(f"Running soda on {self.dq_config['engine']}")
#         else:
#             raise ValueError('Invalid value for engine. Should be either databricks/dremio/spark')
#         return config

#     def _run_spark(self):
#         print('Running Spark')

#     def execute_check(self):
#         """
#         Execute Soda Check Run using the correct engine.

#         Check which engine to run the check on instantiates the respective Scan class.
#         Then, calls the run method of the Scan class.
#         """
#         engine_config = self._get_engine_config()
#         for each in self.dq_config['details']:
#             dq_config = self.dq_config
#             dq_config['details'] = each
#             if self.dq_config['engine'] == 'dremio':
#                 self.logger.info('Initializing Dremio Scan')
#                 soda_scan = DremioSodaScan(dq_config=dq_config, engine_config=engine_config)
#                 soda_scan.run_dq()
#             elif self.dq_config['engine'] == 'databricks':
#                 self.logger.info('Initializing Databricks Scan')
#                 soda_scan = DatabricksSodaScan(dq_config=dq_config, engine_config=engine_config)
#                 soda_scan.run_dq()
#             else:
#                 self.logger.info(f'Running Soda on Spark')
#                 # raise NotImplementedError('Spark Submit Has Not Been Implemented Yet')
#                 self._run_spark()
#             # spark_submit(spark_script, self.cluster_id, self.engine, self.check_dict, self.dataset_dict)

#     def check_failures(self):
#         """
#         Check Failures in S3 and sends alerts.

#         Read results from s3 and checks for failures.
#         Converts failures into a dict for logging in sentry and alation.
#         :return results: Dict
#             Failures results for the Scan.
#         """
#         self.logger.info('Checking Failures')
#         storage_connector = S3Connector()
#         storage = S3Storage(connector=storage_connector, bucket=self.dq_config['result_bucket'])
#         data = storage.read(path=self.dq_config['result_path_with_timestamp'])
#         data = json.loads(data)
#         storage_connector.disconnect()
#         results = dict(execution_uuid=self.dq_config['execution_uuid'], check_class=[], inputs={'check_definition': []},
#                        outputs=[], column_name=[], pipeline_stage=self.dq_config.get('stage', None),
#                        schema_name=self.dq_config.get('schema_name', None),
#                        table_name=self.dq_config.get('table_name', None), results=[],
#                        result_path=self.dq_config['result_path_with_timestamp'])
#         for each in data:
#             if each['result'] in ['fail', 'warn'] and each['execution_uuid'] == self.dq_config['execution_uuid']:
#                 if each['column']:
#                     results['check_class'].append(f"{each['check_name']}({each['column']})")
#                 else:
#                     results['check_class'].append(f"{each['check_name']}({each['check_definition']})")
#                 results['column_name'].append(each['column'])
#                 results['inputs']['check_definition'].append(each['check_definition'])
#                 results['outputs'].append(each['check_value'])
#                 results['results'].append(each['result'])

#         self.logger.info(
#             f"DQ RESULT PATH - {self.dq_config['result_bucket']}/{self.dq_config['result_path_with_timestamp']}")
#         self.logger.info(f"DQ EXECUTION UUID - {self.dq_config['execution_uuid']}")

#         if not results['outputs']:
#             results = None
#         return results

#     def slack_notification(self):
#         """Send Slack Notification for failures."""
#         self.logger.info('Slack Notification')
#         raise NotImplementedError('Slack Notification Not Implemented')

#     def sentry_notification(self):
#         """Send Sentry Notification for failures."""
#         self.logger.info('Sentry Notification')
#         raise NotImplementedError('Sentry Notification Not Implemented')

#     def alation_warning(self):
#         """Raise Alation Warning for failures."""
#         self.logger.info('Alation Warning')
#         raise NotImplementedError('Alation Warning Not Implemented')


from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2023, 4, 3)
}

dag = DAG(
    'aa_pip_freeze_dag',
    default_args=default_args,
    schedule_interval=None
)

print_pip_freeze = BashOperator(
    task_id='print_pip_freeze',
    bash_command='pip freeze',
    dag=dag
)

print_pip_freeze
