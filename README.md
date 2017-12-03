# assets-pricer

Download and store daily prices for all the traded assets in a portfolio. It is intended to be deployed onto AWS Lambda.

### Quick Deployment on AWS Lambda

Setup and activate a virtual environment.

    # virtualenv -p /usr/bin/python3.6 myenv
    # source myenv/bin/activate

Install all dependencies using pip.

    # pip install -r requirements.txt

Build the Lambda package zip.

    # mkdir package
    # cp -rf $VIRTUAL_ENV/lib/python3.6/site-packages/* package
    # cp -rf assetspricer package
    # cp assets-pricer.ini lambda_function.py package
    # cd package
    # zip -r package.zip .

Deploy on S3 using the CLI or the AWS Console, then create a Lambda function from the package.

### Configure assets-pricer

Create or modify the assets-pricer.ini file in order to configure assets-pricer:

        [database]
        db_host=domain.com
        db_name=database
        db_user=username
        db_pass=l33tp4ssw0rd

### Authors

Jean de Kernier <jean.dekernier@gmail.com>

### License

This software comes under the terms of the MIT license. See the LICENSE file for the complete text of the license.
