# GH Collaborative Data

## Prerequisites

- Docker
- docker-compose
- Python 3.9
- virtualenv

## Setup local environment
Not needed to run, only to contribute (add changes)
```shell script
git clone git@github.com:vschettino/gh-collaborative-data.git
cd gh-collaborative-data
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
Then open the project with your favourite IDE.

## Running

```shell script
cp env.example .env # change the root password!
docker-compose up # the script will run once
docker-compose run script # run whenever you need. Source code is automatically mapped into the container, no need to rebuild.
```

Adminer (former phpMinAdmin) will be available at http://localhost:8080