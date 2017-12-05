from decimal import Decimal

import requests


class CheckoutApi:
    '''
    Wraps Checkout's HTTP API and tracks the token used for authentication.
    '''

    def __init__(self, token=None, server=None):
        self.token = token
        self.server = server

        self.auth = {'token': self.token}

    def check_token(self):
        ''' Assert that we have something to connect to. '''
        if not self.server or not self.token:
            raise CheckoutException('No token or server set, cannot connect!')
        return True

    def get_products(self):
        ''' Get the products currently available. '''

        self.check_token()
        r = requests.get(f'{self.server}/api/checkout/products',
                params=self.auth)

        response = r.json()
        result = [CheckoutProduct(p) for p in response]
        return result

    def get_card(self, card_id):
        ''' Get the information associated with a Card, if it exists. '''
        self.check_token()

        params = {**self.auth, 'uuid': card_id}
        r = requests.get(f'{self.server}/api/checkout/card', params=params)

        response = r.json()
        return CheckoutUser(self, response)

    def create_card(self, card_id, student_id):
        '''
        Request a new Card to be created and linked to the given student.
        '''
        self.check_token()

        params = {
            **self.auth,
            'uuid': card_id,
            'student': student_id
        }

        r = requests.post(
            f'{self.server}/api/checkout/card',
            params=params
        )

        if r.status_code >= 400:
            raise CheckoutException(
                f'CheckoutException: {r.status_code} {r.response_text}'
            )

class CheckoutProduct:
    '''
    Wraps the products from Checkout and makes a nice Python object.
    '''

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.category = data['category']
        self.price = Decimal(data['price'])
        self.image = data['image']

    def __repr__(self):
        return f"<CheckoutProduct: {self.name} ({self.id}, €{self.price})>"

class CheckoutUser:
    '''
    Wraps the returned data about a User.
    '''

    def __init__(self, api, data):
        self.api = api
        self.id = data['id']
        self.uuid = data['uuid']
        self.first_name = data['first_name']
        self.balance = Decimal(data['balance'])

    def purchase(self, cart):
        ''' Purchase the given products. '''
        ids = [p.id for p in cart]

        params = {**self.api.auth, 'items': ids, 'uuid': self.uuid}
        r = requests.post(
            f'{self.api.server}/api/checkout/transaction',
            params=params
        )

        if r.status_code >= 400:
            raise CheckoutException(
                f'CheckoutException: {r.status_code} {r.response_text}'
            )

        response = r.json()
        self.balance = Decimal(response['balance'])

    def __repr__(self):
        return f"<CheckoutUser: {self.first_name} ({self.id}/{self.uuid})>"

class CheckoutException(Exception):
    pass
