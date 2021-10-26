# Dani Exchange

To build the project in a closed environment you only need to have docker installed on your computer.

When you have the cloned repository and you are in the root of the project, create the docker containers:
> docker-compose up

This will create the images and raise the corresponding containers, if we want to enter in the main container we can execute the following command:
> docker exec -ti dani_exchange_web bash

# Project configuration

To use Fixer you must cover the following field included in settings.py:

* FIXER_KEY

When you create a free Fixer account, you will receive your password.

# Execute tests

Once inside the container we can launch the unit tests with the following command:
> python3 /opt/dani_exchange/dani_exchange/manage.py test dani_exchange

This executes the tests located in '/opt/dani_exchange/dani_exchange/dani_exchange/tests/'.

# Main features of the project

The project periodically queries the exchange rates of the different currencies enabled, this is done daily in a scheduled task, or at the time of a query if necessary. These queries are made to providers that can be changed through the Provider Model and their use is defined according to a priority field.

We have three available services, which allow us to know the exchange rates of a currency in a period of time, to calculate the exchange rate of an amount of money between two currencies, or to know the time-weighted rate of an amount of money for a given date.

The endpoints can be seen in detail in the url: http://localhost:8000/swagger/

# Other details

When you create the containers, a series of fixtures will be automatically loaded with the minimum data of users, OAuth2 application, OAuth2 token, Providers, Currencies and periodic tasks. This is a minimum information to be able to test the project as soon as possible.

Fixture user data:
* admin / 123456
* api_user / EJH2y8dBMCvfVq2W
