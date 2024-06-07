#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DataIngestionStack } from '../lib/data-ingestion-stack';

const app = new cdk.App();
new DataIngestionStack(app, 'DataIngestionStack', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});