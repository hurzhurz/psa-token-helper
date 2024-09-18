# Experiment to automate token generation
This is a modified version that controls the browser by injecting javascript to fill out and submit the login form. Just to test if it is possible.
With docker it is possible to run it headless.

Error handling is very limited. If something goes wrong, it simply runs into a timeout while waiting for an expected state.
If it runs on a machine with limited performance, it might be necessary to increase the timeout.

## Usage
1. Build the docker image (only needed once):
`docker build -t psa-token-helper-auto .`

2. Run image to get tokens:
`docker run -it --rm psa-token-helper-auto -b BRAND -u USERNAME -p PASSWORD`

## Example outputs

###  Show possible parameters:
```
# docker run -it --rm psa-token-helper-auto --help
usage: psa-token-helper-auto.py [-h] -b {citroen,ds,opel,peugeot} -u USERNAME -p PASSWORD [-c COUNTRYCODE] [-t TIMEOUT]

Automated PSA Token Helper

options:
  -h, --help            show this help message and exit
  -b {citroen,ds,opel,peugeot}, --brand {citroen,ds,opel,peugeot}
                        Vehicle brand (default: None)
  -u USERNAME, --username USERNAME
                        Username (default: None)
  -p PASSWORD, --password PASSWORD
                        Password (default: None)
  -c COUNTRYCODE, --countrycode COUNTRYCODE
                        Countrycode (default: de)
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout between each step (default: 15)
```

### Successful:
```
# docker run -it --rm psa-token-helper-auto -b opel -u aaa@bbb.de -p xyz ; echo "result code: "$?
{
    "access_token": "xxx",
    "refresh_token": "xxx",
    "scope": "openid profile",
    "id_token": "xxx",
    "token_type": "Bearer",
    "expires_in": 3599
}
result code: 0
```

### Unsuccessful (e.g. wrong password):
```
# docker run -it --rm psa-token-helper-auto -b opel -u aaa@bbb.de -p xyz ; echo "result code: "$?
Y4cd68 ; echo "result code: "$?
timeout
result code: 1
```
