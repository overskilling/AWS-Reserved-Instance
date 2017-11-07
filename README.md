# Get AWS REserved Instance Coverage

This script summarises the current usage by instance type in each region and compares this against the active
reserved instances in that region. 

Currently the script checks EC2 and RDS instances. 

## Usage

  getRICoverage.py

## Sample Output 
```
 RDS
=====

    eu-west-2
   ===========
   db.m4.large  Usage:  4 Reserved:  4 : ✓
   db.r3.large  Usage:  1 Reserved:  1 : ✓
  db.r4.xlarge  Usage:  1 Reserved:  1 : ✓
  db.t2.medium  Usage:  2 Reserved:  0 : ❌
   db.t2.micro  Usage:  1 Reserved:  0 : ❌

 EC2
=====

    eu-west-2
   ===========
      m4.large  Usage: 18 Reserved: 30 : ✓
     m4.xlarge  Usage:  3 Reserved:  3 : ✓
     t2.medium  Usage:  4 Reserved:  4 : ✓
      t2.micro  Usage:  1 Reserved:  2 : ✓
      t2.small  Usage:  1 Reserved:  1 : ✓

```

## Todo

+ For RDS the AZ Type must match the RI purchased type itherwise it doesn't count as a match 