#!/usr/bin/env python3
# coding: utf-8
'''
  Get the Reserved Instance Usage for each region
'''
from collections import Counter
import boto3
from termcolor import colored

def getAllRegions():
    ec2 = boto3.client('ec2', region_name='eu-west-1')
    response = ec2.describe_regions()
    return response['Regions']

def getAllInstances(regions, type):
    # Get all of the regions
    imapping = { 'elasticache' : 'CacheClusters',  'rds' : 'DBInstances' }
    instances = []
    for region in regions:
        client = boto3.client(type, region_name=region['RegionName'])
        # Add the region to each result 
        if type == 'elasticache':
            for i in client.describe_cache_clusters()[imapping[type]]:
                i['Region'] = region['RegionName']
                instances.append(i)
        elif type == 'rds':
            for i in client.describe_db_instances()[imapping[type]]:
                i['Region'] = region['RegionName']
                instances.append(i)
        else:
            for i in client.describe_instances()[imapping[type]]:
                i['Region'] = region['RegionName']
                instances.append(i)
    # All done
    return instances

def getAllCacheReservedInstances(regions):
    instances = []
    for region in regions:
        client = boto3.client('elasticache', region_name=region['RegionName'])
        # Add the region - no filters for RDS so we filter by hand 
        for i in client.describe_reserved_cache_nodes()['ReservedCacheNodes']:
            if i['State'] == 'active' :
                i['Region'] = region['RegionName']
                instances.append(i)
    return instances

def getAllRDSReservedInstances(regions):
    instances = []
    for region in regions:
        rds = boto3.client('rds', region_name=region['RegionName'])
        # Add the region - no filters for RDS so we filter by hand 
        for i in rds.describe_reserved_db_instances()['ReservedDBInstances']:
            if i['State'] == 'active' :
                i['Region'] = region['RegionName']
                instances.append(i)
    return instances

def getAllEC2Instances(regions):
    # This has a different structure than the other services
    # Get all of the regions
    instances = []
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region['RegionName'])
        # Add the region
        for e in ec2.describe_instances()['Reservations']:
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
    instances = getAllInstances(regions,'rds')
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
                print('  %15s  Usage: %2d Reserved: %2d : %s' % (db[0], usage[db[0]], reserved[db[0]], status))

def CacheReport():
    regions = getAllRegions()
    instances = getAllInstances(regions,'elasticache')
    reserved_instances = getAllCacheReservedInstances(regions)

    print("\n Cache\n =====")
    # Now see if we have enough of each type
    for region in regions:
        usage = Counter([ x['CacheNodeType'] for x in
                          [ i for i in instances if i['Region'] == region['RegionName']]])
        # Do we have any instances?
        if len(usage) > 0:
            print('\n {:^15s}\n {:^15s}'.format(region['RegionName'], '=' * (len(region['RegionName'])+2)))
            # Multiple reserved instances of the same type so sum them up
            reserved = Counter()
            for instance in [ i for i in reserved_instances if i['Region'] == region['RegionName'] ]:
                reserved[instance['CacheNodeType']] += instance['CacheNodeCount']
            # Okay ready for the output
            for cache in sorted(usage.items()):
                if usage[cache[0]]>reserved[cache[0]]:
                    status = colored(u'\u274C', 'red')
                else:
                    status = colored(u'\u2713', 'green')
                print('  %12s  Usage: %2d Reserved: %2d : %s' % (cache[0],usage[cache[0]],reserved[cache[0]],status))


def main():
    '''Elasticache, EC2 and RDS Reserved Instance Coverage Report'''
    CacheReport()
    EC2Report()
    RDSReport()
    
if __name__ == '__main__':
    main()
