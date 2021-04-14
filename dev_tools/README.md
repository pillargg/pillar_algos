# Dev Tools

Common functions to help in developing `pillaralgos` library. Includes 
* `dev_helpers.awsBucketAPI` to connect to aws (assuming AWS Cli is installed locally), download files.
* `dev_helpers.plot_with_time` to create a time series plot with conveniently formatted xaxis
* `sanity_checks` future site of error catchers

# How To
Connect to AWS bucket, download random files.
```
from pillaralgos_dev import dev_helpers as dev
aws = dev.awsBucketAPI()
names = aws.get_random_file_names(n=5)
aws.save_files(names)
```
Check sanity:
```
from pillaralgos_dev import sanity_checks as sane
```