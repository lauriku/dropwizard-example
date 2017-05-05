import boto3
import sys

autoscaling_conn = boto3.client('autoscaling')

response = autoscaling_conn.describe_auto_scaling_groups(
            AutoScalingGroupNames=[sys.argv[1]])

instances = [] 
elb = ""
for asg in response['AutoScalingGroups']:
    for instance in asg['Instances']:
        instances.append({'InstanceId': instance['InstanceId']})
    elb = asg['LoadBalancerNames'][0]

elb_conn = boto3.client('elb')

instance_in_service_waiter = elb_conn.get_waiter('instance_in_service')

instance_in_service_waiter.wait(LoadBalancerName=elb, Instances=instances)

