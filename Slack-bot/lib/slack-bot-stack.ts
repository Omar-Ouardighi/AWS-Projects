import {aws_lambda as lambda, aws_iam as iam, aws_dynamodb as dynamodb} from 'aws-cdk-lib';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {slack_token} from './constants';

export class SlackBotStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const botLambda = new lambda.Function(this, 'SlackBotLambda', {
      functionName: 'SlackBotLambda',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'main.handler',
      timeout: cdk.Duration.seconds(30),
      retryAttempts: 0,
      environment: {
        'SLACK_TOKEN': slack_token 
      },
      role: new iam.Role(this, 'SlackBotLambdaRole', {
        assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
        managedPolicies: [
          iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
          iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'),
        ],
        inlinePolicies: {
          'DynamoDBPolicy': new iam.PolicyDocument({
            statements: [
              new iam.PolicyStatement({
                actions: ['dynamodb:*'],
                resources: ['*'],
              }),
            ],
          }),
        },
        
  }),     
})
  // setup lambda url
   const lambdaUrl = botLambda.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
    })

    //  print lambda url after deployment
    new cdk.CfnOutput(this, 'FunctionUrl ', { value: lambdaUrl.url });

    // create dynamodb table
    const table = new dynamodb.Table(this, 'SlackBotTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      tableName: 'SlackBotTable',
      billingMode:dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
    });
}}
