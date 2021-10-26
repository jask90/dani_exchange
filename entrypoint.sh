#!/bin/sh

sleep 10

if test ! -f /opt/dani_exchange/.first.txt;
then
    rm -rf /opt/dani_exchange/dani_exchange/migrations
    python3 /opt/dani_exchange/dani_exchange/manage.py collectstatic --no-input
    python3 /opt/dani_exchange/dani_exchange/manage.py flush --no-input
    python3 /opt/dani_exchange/dani_exchange/manage.py makemigrations dani_exchange
    python3 /opt/dani_exchange/dani_exchange/manage.py migrate

    python3 /opt/dani_exchange/dani_exchange/manage.py loaddata /opt/dani_exchange/dani_exchange/dani_exchange/fixtures/currencies.json
    python3 /opt/dani_exchange/dani_exchange/manage.py loaddata /opt/dani_exchange/dani_exchange/dani_exchange/fixtures/providers.json
    python3 /opt/dani_exchange/dani_exchange/manage.py loaddata /opt/dani_exchange/dani_exchange/dani_exchange/fixtures/users.json
    python3 /opt/dani_exchange/dani_exchange/manage.py loaddata /opt/dani_exchange/dani_exchange/dani_exchange/fixtures/applications.json
    python3 /opt/dani_exchange/dani_exchange/manage.py loaddata /opt/dani_exchange/dani_exchange/dani_exchange/fixtures/accesstokens.json
    python3 /opt/dani_exchange/dani_exchange/manage.py loaddata /opt/dani_exchange/dani_exchange/dani_exchange/fixtures/crontabs.json
    python3 /opt/dani_exchange/dani_exchange/manage.py loaddata /opt/dani_exchange/dani_exchange/dani_exchange/fixtures/periodictasks.json

    touch /opt/dani_exchange/.first.txt;
else
    /usr/bin/pip3 install -r /opt/dani_exchange/requirements.txt
    python3 /opt/dani_exchange/dani_exchange/manage.py collectstatic --no-input
fi

exec "$@"