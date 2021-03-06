Title: Installation

#How to Install FlowKit

There are three main ways to install FlowKit.

* [Quick install](#quickinstall); suitable for a try-out on a local PC, includes basic example using FlowClient.
* [Developer install](#developers); for those wishing to contribute code
* [Production install](#prodinstall); for deployment, e.g. inside an MNO firewall 

 <a name="quickinstall">

## Quick Install

This quick install guide will install the major components of FlowKit together with an intial setup and example analysis query.

The bulk of the installation process consists of downloading [Docker](https://docs.docker.com/install/) containers from [DockerCloud](https://cloud.docker.com/), using [Docker Compose](https://docs.docker.com/compose/). Followed by a pip install of FlowClient.

These instructions assume use of [Pyenv](https://github.com/pyenv/pyenv) and [Pipenv](https://github.com/pypa/pipenv). [Anaconda](https://www.anaconda.com/what-is-anaconda/) stack based installation commands may be different. 


### Server and Authentication Installation

Docker containers for FlowAPI, FlowMachine and FlowDB are provided in the [DockerCloud](https://cloud.docker.com/) repositories `flowminder/flowapi`, `flowminder/flowmachine` and `flowminder/flowdb`, respectively. You will need [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/).

Create a directory for your FlowKit install and move into it. Download the [`docker-compose.yml`](https://github.com/Flowminder/FlowKit/raw/master/docker-compose.yml) file.

```
wget https://raw.githubusercontent.com/Flowminder/FlowKit/master/docker-compose.yml
```
Note, it is possible to replace `master` in the above url to install other releases.

The compose file expects the `JWT_SECRET_KEY` environment variable to be set. It is used on FlowAuth and FlowAPI to sign and verify access to the API.

Start the FlowKit test system by running 
```bash
JWT_SECRET_KEY=secret docker-compose up -d
``` 
This will pull any necessary docker containers, and start the system in the background with the API exposed on port `9090` by default.  

In order to use the test system, now install FlowClient and FlowAuth. 

### Installing FlowAuth

FlowAuth must be installed to provide centralised token based authentication management for FlowKit systems.


#### FlowAuth Quickstart

To run a demonstration version of FlowAuth use:

```bash
docker run -p 8000:80 -e DEMO_MODE=1 flowminder/flowauth
```

This will start FlowAuth at <a href="http://localhost:8000/" target="_blank">http://localhost:8000</a>, and pre-populate a disposable sqlite database with some dummy data. Log in with either `TEST_ADMIN:DUMMY_PASSWORD` or `TEST_USER:DUMMY_PASSWORD`.

#### Granting user permissions in FlowAuth

The following steps using the FlowAuth administration tool are required to add a user and allow them to generate access tokens to communicate with a FlowKit server through FlowAPI:

1. Log into FlowAuth as an administrator.

2. Under "API Routes", add any applicable API routes (e.g. `daily_location`).

3. Under "Aggregation Units", add any applicable aggregation units (e.g. `admin3`).

3. Under "Servers", add a new server and give it a name and secret key. Note that the Secret Key must match the `JWT_SECRET_KEY` set in the flowapi docker container on this server ('secret' in the example above).

4. Enable any permissions for this server under "API Permissions", and aggregation units under "Aggregation Units".

5. Under "Users", add a new user, and set the username and password.

6. Either:
    - Add a server to the user, and enable/disable API permissions and aggregation units,
    <p>
7. Or:
    <p>
    - Under "Groups", add a new group,

    - Add a server to the group, and enable/disable API permissions and aggregation units,

    - Add the user to the group.


The user can then log into FlowAuth and generate a token (see the [analyst section](3-analyst.md#flowauth) for instructions).


### FlowClient <a name="flowclient"> </a>

The FlowClient Python client is used to perform CDR analysis using the JupyterLab Python Data Science Stack. It may be installed using pip:

```bash
pip install flowclient
```

Quick install is continued with an example of FlowClient usage [here](3-analyst.md#flowclient).

<a name="developers">

## Developer Install</a>

After cloning the [GitHub repository](https://github.com/Flowminder/FlowKit), the FlowKit system can be started by running `make up` in the root directory. This requires [Docker](https://docs.docker.com/install/) and [Docker Compose](https://docs.docker.com/compose/install/) to be installed, and starts the flowapi, flowmachine, flowdb and redis docker containers using the `docker-compose-dev.yml` file.

FlowKit uses [pipenv](https://pipenv.readthedocs.io/) to manage Python environments. To start a Python session in which you can use FlowClient:

```
cd flowclient
pipenv install
pipenv run python
>>> import flowclient
```

To run the tests in the `flowapi`, `flowclient`, `flowdb`, `flowmachine` or `integration_tests` directory:

```bash
cd <directory>
pipenv install --dev
pipenv run pytest
```


 <a name="prodinstall">

## Production Install 

Contact Flowminder on [flowkit@flowminder.org](mailto:flowkit@flowminder.org) for full instructions. Instructions on FlowAuth production deployment and dealing with docker secrets is described below. Note that these instructions are likely subject to change.


### FlowAuth Production Deployment

FlowAuth is designed to be deployed as a single Docker container working in cooperation with a database and, typically, an ssl reverse proxy (e.g. [nginx-proxy](https://github.com/jwilder/nginx-proxy) combined with [letsencrypt-nginx-proxy-companion](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion)).

FlowAuth supports any database supported by [SQLAlchemy](https://sqlache.me), and to connect you will only need to supply a correct URI for the database either using the `DB_URI` environment variable, or by setting the `DB_URI` secret. If `DB_URI` is not set, a temporary sqlite database will be created.

On first use, you will need to create the necessary tables and an administrator account. 

To initialise the tables, you can either set the `INIT_DB` environment variable to `true`, or run `flask init-db` from inside the container (`docker exec <container-id> flask init-db`).

To create an initial administrator, use the `ADMIN_USER` and `ADMIN_PASSWORD` environment variables or set them as secrets. Alternatively, you may run `flask add-admin <username> <password>` from inside the container. You can combine these environment variables with the `INIT_DB` environment variable.

You _must_ also provide two additional environment variables or secrets: `FERNET_KEY`, and `SECRET_KEY`. `FERNET_KEY` is used to encrypt server secret keys, and tokens while 'at rest' in the database, and decrypt them for use. `SECRET_KEY` is used to secure session, and CSRF protection cookies.

By default, `SECRET_KEY` will be set to `secret`. You should supply this to ensure a secure system.

While `SECRET_KEY` can be any arbitrary string, `FERNET_KEY` should be a valid Fernet key. A convenience command is provided to generate one - `flask get-fernet`.  


#### Running with Secrets

The standard Docker compose file supplies a number of 'secret' values as environment variables. Typically, this is a bad idea.

Instead, you should make use of [docker secrets](https://docs.docker.com/engine/swarm/secrets/), which are stored securely in docker and only made available _inside_ containers.  The `secrets_quickstart` directory contains a [docker _stack_](https://docs.docker.com/docker-cloud/apps/stack-yaml-reference/) file (`docker-stack.yml`). The stack file is very similar to a compose file, but removes container names, and adds a new section - secrets.

The stack expects you to provide seven secrets:

 - cert-flowkit.pem
 
    An SSL certificate file (should contain private key as well)

 - API_DB_USER
 
    The username the API will use to connect to FlowDB

 - API_DB_PASS
 
    The password that the API will use to connect to FlowDB

 - FM_DB_USER
 
    The username that FlowMachine will use to connect to FlowDB

 - FM_DB_PASS 
 
    The password that FlowMachine will use to connect to FlowDB

 - POSTGRES_PASSWORD_FILE
 
    The superuser password for the `flowdb` user 

 - JWT_SECRET_KEY
 
    The secret key used to sign API access tokens
    

To make use of secrets you will need to use docker swarm. For testing purposes, you can set up a single node swarm by running `docker swarm init`.

Once you have created a swarm, you can add secrets to it using the [docker secret](https://docs.docker.com/engine/reference/commandline/secret_create/) command. For example, to add a randomly generated password for the `FM_DB_PASS` secret:

```bash
openssl rand -base64 16 | docker secret create FM_DB_PASS -
```

And to add the (unsigned) localhost SSL certificate supplied in the `integration_tests` directory:

```bash
docker secret create cert-flowkit.pem integration_tests/cert.pem
```

(Note that unlike the other examples, we are supplying a _file_ rather than piping to stdin.)

Once you have added all five required secrets, you can use `docker stack` to spin up FlowKit, much as you would `docker-compose`:

```bash
cd secrets_quickstart
docker stack deploy --with-registry-auth -c docker-stack.yml secrets_test
```

After which, the API will be available via HTTPS (and no longer available via HTTP). Note that to access the API using FlowClient, you'll need to provide the path to the certificate as the `ssl_certificate` argument when calling `flowclient.Connection` (much as you would if using a self-signed certificate with `requests`):

```python
import flowclient
conn = flowclient.Connection("https://localhost:9090", "JWT_STRING", ssl_certificate="/home/username/flowkit/integration_tests/client_cert.pem")
```

#### Secrets Quickstart

```bash
cd secrets_quickstart
docker login
docker swarm init
openssl rand -base64 16 | docker secret create FM_DB_PASS -
echo "fm" | docker secret create FM_DB_USER -
echo "api" | docker secret create API_DB_USER -
openssl rand -base64 16 | docker secret create API_DB_PASS -
openssl rand -base64 16 | docker secret create POSTGRES_PASSWORD_FILE -
openssl req -newkey rsa:4096 -days 3650 -nodes -x509 -subj "/CN=flow.api" \
    -extensions SAN \
    -config <( cat $( [[ "Darwin" -eq "$(uname -s)" ]]  && echo /System/Library/OpenSSL/openssl.cnf || echo /etc/ssl/openssl.cnf  ) \
    <(printf "[SAN]\nsubjectAltName='DNS.1:localhost,DNS.2:flow.api'")) \
    -keyout cert.key -out cert.pem
cat client_cert.key cert.pem > cert-flowkit.pem
docker secret create cert-flowkit.pem cert-flowkit.pem
echo "secret" | docker secret create JWT_SECRET_KEY -
docker stack deploy --with-registry-auth -c docker-stack.yml secrets_test
```

This will bring up a single node swarm, create random 16 character passwords for the database users, generate a certificate valid for the `flowkit.api` domain (and point that to `localhost` using `/etc/hosts`), pull all necessary containers, and bring up the API with `secret` as the JWT secret key.

For convenience, you can also do `pipenv run secrets_quickstart` from the `secrets_quickstart` directory.

Note that if you wish to deploy a branch other than master, you should set the `CIRCLE_BRANCH` environment variable before running, to ensure that Docker pulls the correct tags.

You can then provide the certificate to `flowclient`, and finally connect via https:

```python
import flowclient
conn = flowclient.Connection("https://localhost:9090", "JWT_STRING", ssl_certificate="<path_to_cert.pem>")
```

(This generates a certificate valid for the `flow.api` domain as well, which you can use by adding a corresponding entry to your `/etc/hosts` file.)