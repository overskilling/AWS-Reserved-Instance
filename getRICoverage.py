#!/usr/bin/env python
# coding: utf-8
#
from collections import Counter
import boto3
from termcolor import colored, cprint

def getAllRegions():
    ec2 = boto3.client('ec2', region_name='eu-west-1')
    response = ec2.describe_regions()
    return response['Regions']

def getAllRDSInstances(regions):
    # Get all of the regions
    instances = []
    for region in regions:
        rds = boto3.client('rds', region_name=region['RegionName'])
        # Add the region
        for i in rds.describe_db_instances()['DBInstances']:
            i['Region'] = region['RegionName']
            instances.append(i)
    return instances

def getAllRDSReservedInstances(regions):
    instances = []
    for region in regions:
        rds = boto3.client('rds', region_name=region['RegionName'])
        # Add the region - no filters for RDS
        for i in rds.describe_reserved_db_instances()['ReservedDBInstances']:
            i['Region'] = region['RegionName']
            instances.append(i)
    return instances

def getAllEC2Instances(regions):
    # Get all of the regions
    instances = []
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region['RegionName'])
        # Add the region
        response = ec2.describe_instances()
        ec2List = response['Reservations']
        for e in ec2List:
            for i in e['Instances']:
                i['Region'] = region['RegionName']
                instances.append(i)
    return instances

def getAllEC2ReservedInstances(regions):
    instances = []
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region['RegionName'])
        # Add the region
        filter = {'Name': 'state', 'Values':['active']}
        for i in ec2.describe_reserved_instances(Filters=[filter])['ReservedInstances']:
            i['Region'] = region['RegionName']
            instances.append(i)
    return instances

def EC2Report():
    regions = getAllRegions()
    instances = getAllEC2Instances(regions)
    reserved_instances = getAllEC2ReservedInstances(regions)

    print("\n EC2\n=====")
    # Now see if we have enough of each type
    for region in regions:
        usage = Counter([ x['InstanceType'] for x in
                          [ i for i in instances if i['Region'] == region['RegionName']]])
        # Do we have any instances?
        if len(usage) > 0:
            print('\n {:^15s}\n {:^15s}'.format(region['RegionName'], '=' * (len(region['RegionName'])+2)))
            # Multiple reserved instances of the same type so sum them up
            reserved = Counter()
            for instance in [ i for i in reserved_instances if i['Region'] == region['RegionName'] ]:
                reserved[instance['InstanceType']] += instance['InstanceCount']
            # Okay ready for the output
            for ec2 in sorted(usage.items()):
                if usage[ec2[0]]>reserved[ec2[0]]:
                    status = colored(u'\u274C', 'red')
                else:
                    status = colored(u'\u2713', 'green')
                print('  %12s  Usage: %2d Reserved: %2d : %s' % (ec2[0],usage[ec2[0]],reserved[ec2[0]],status))

def RDSReport():
    regions = getAllRegions()
    instances = getAllRDSInstances(regions)
    reserved_instances = getAllRDSReservedInstances(regions)

    print("\n RDS\n=====")
    # Now see if we have enough of each type
    for region in regions:
        usage = Counter([ x['DBInstanceClass'] for x in [ i for i in instances if i['Region'] == region['RegionName']]])
        # Do we have any instances?
        if len(usage) > 0:
            print('\n {:^15s}\n {:^15s}'.format(region['RegionName'], '=' * (len(region['RegionName'])+2)))
            # Multiple reserved instances of the same type so sum them up
            reserved = Counter()
            for instance in [i for i in reserved_instances if i['Region'] == region['RegionName']]:
                reserved[instance['DBInstanceClass']] += instance['DBInstanceCount']
            # Okay ready for the output
            for db in sorted(usage.items()):
                if usage[db[0]] > reserved[db[0]]:
                    status = colored(u'\u274C', 'red')
                else:
                    status = colored(u'\u2713', 'green')
                print('  %12s  Usage: %2d Reserved: %2d : %s' % (db[0], usage[db[0]], reserved[db[0]], status))

def main():
    '''EC2 and RDS Reserved Instance Coverage Report'''
    RDSReport()
    EC2Report()

if __name__ == '__main__':
    main()
