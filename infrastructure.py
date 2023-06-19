from aws_cdk import core
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3_notifications as s3n
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam


class S3LambdaGlueStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create source S3 bucket
        source_bucket = s3.Bucket(self, 'SourceBucket', removal_policy=core.RemovalPolicy.DESTROY)

        # Create target S3 bucket
        target_bucket = s3.Bucket(self, 'TargetBucket', removal_policy=core.RemovalPolicy.DESTROY)

        # Create Glue IAM role with necessary permissions
        glue_role = iam.Role(self, 'GlueRole',
                             assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),
                             managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSGlueServiceRole')])

        # Create Glue job
        glue_job = glue.CfnJob(self, 'GlueJob',
                               role=glue_role.role_arn,
                               command=glue.CfnJob.JobCommandProperty(name='glueetl',
                                                                     python_version='3',
                                                                     script_location='s3://<script-bucket>/<script-key>.py'),
                               default_arguments={
                                   '--enable-metrics': '',
                                   '--enable-glue-datacatalog': '',
                                   '----additional-python-modules': '',
                                   '----extra-jars': ''
                               })

        # Create Lambda function
        lambda_fn = _lambda.Function(self, 'LambdaFunction',
                                     runtime=_lambda.Runtime.PYTHON_3_8,
                                     handler='index.handler',
                                     code=_lambda.Code.from_asset('lambda'),
                                     environment={
                                         'GLUE_JOB_NAME': glue_job.ref,
                                         'TARGET_BUCKET_NAME': target_bucket.bucket_name
                                     })

        # Configure S3 bucket notification for Lambda trigger
        source_bucket.add_event_notification(s3.EventType.OBJECT_CREATED,
                                             s3n.LambdaDestination(lambda_fn))


app = core.App()
S3LambdaGlueStack(app, 'S3LambdaGlueStack')
app.synth()
