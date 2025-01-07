# hephaestus-business-logic-layer

## Install python dependecies

create a virtual environment for python

```bash
python3 -m venv .venv
```

Activate the virtual .env

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip3 install -r requirements.txt
```

## BASH script


To execute the deployment script, run the following command:

```bash
bash deploy.sh --env dev --profile loquesea --region us-west-2
```