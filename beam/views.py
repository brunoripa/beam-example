import os
import logging
import flask
from flask import views
import apache_beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import StandardOptions
from apache_beam.io.textio import ReadFromText, WriteToText


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Split(apache_beam.DoFn):

    def process(self, element):
        """
        Splits each row on commas and returns a dictionary representing the
        row
        """
        country, duration, user = element.split(",")

        return [{
            'country': country,
            'duration': float(duration),
            'user': user
        }]


class CollectTimings(apache_beam.DoFn):

    def process(self, element):
        """
        Returns a list of tuples containing country and duration
        """

        result = [
            (element['country'], element['duration'])
        ]
        return result


class CollectUsers(apache_beam.DoFn):

    def process(self, element):
        """
        Returns a list of tuples containing country and user name
        """
        result = [
            (element['country'], element['user'])
        ]
        return result


class WriteToCSV(apache_beam.DoFn):

    def process(self, element):
        """
        Prepares each row to be written in the csv
        """
        result = [
            "{},{},{}".format(
                element[0],
                element[1]['users'][0],
                element[1]['timings'][0]
            )
        ]
        return result


class FromTextView(views.MethodView):

    def get(self):
        """
        Flask view that triggers the execution of the pipeline
        """
        input_filename = 'input.txt'
        output_filename = 'output.txt'

        # project_id = os.environ['DATASTORE_PROJECT_ID']
        # credentials_file = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        # client = datastore.Client.from_service_account_json(credentials_file)

        options = PipelineOptions()
        gcloud_options = options.view_as(GoogleCloudOptions)
        # gcloud_options.project = project_id
        gcloud_options.job_name = 'test-job'

        # Dataflow runner
        runner = os.environ['DATAFLOW_RUNNER']
        options.view_as(StandardOptions).runner = runner

        with apache_beam.Pipeline(options=options) as p:
            rows = (
                p |
                ReadFromText(input_filename) |
                apache_beam.ParDo(Split())
            )

            timings = (
                rows |
                apache_beam.ParDo(CollectTimings()) |
                "Grouping timings" >> apache_beam.GroupByKey() |
                "Calculating average" >> apache_beam.CombineValues(
                    apache_beam.combiners.MeanCombineFn()
                )
            )

            users = (
                rows |
                apache_beam.ParDo(CollectUsers()) |
                "Grouping users" >> apache_beam.GroupByKey() |
                "Counting users" >> apache_beam.CombineValues(
                    apache_beam.combiners.CountCombineFn()
                )
            )

            to_be_joined = (
                {
                    'timings': timings,
                    'users': users
                } |
                apache_beam.CoGroupByKey() |
                apache_beam.ParDo(WriteToCSV()) |
                WriteToText(output_filename)
            )

        return 'ok'
