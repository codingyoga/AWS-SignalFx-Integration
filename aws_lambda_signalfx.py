import time
import boto3
import logging
import signalfx

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    client = boto3.client('ssm')
    response = client.get_parameters(Names=["signalfx-default-token"],WithDecryption=True)
    SIGNALFX_AUTH_TOKEN = response['Parameters'][0]['Value']
except:
	logging.exception("Error in get signalfx token from ssm")

def lambda_handler(event, context):
	""" Lambda entrypoint. """

	sfx = signalfx.SignalFx().ingest(SIGNALFX_AUTH_TOKEN)
	status = event["detail"].get("state")
	if status == "SUCCEEDED":
		sfx.send(
			gauges=[
			{'metric': 'pipeline.success',
			'value': 1,
			'timestamp': time.time()*1000}
			])
		logger.info('Sending success metrics to signalfx')
	elif status == "FAILED":
		sfx.send(
			gauges=[
			{'metric': 'pipeline.failure',
			'value': 1,
			'timestamp': time.time()*1000}
			])
		logger.info('Sending failure metrics to signalfx')
	sfx.stop()

