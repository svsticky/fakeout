import cmd
import configparser
import os
import readline

from . import api


class FakeoutShell(cmd.Cmd):
    intro = 'Checkout ready! Type `help` or `?` for help.'
    prompt = '(c-o) '
    api = None
    products = None
    cart = None

    def do_getproducts(self, arg):
        ''' Retrieve the current set of available products: GETPRODUCTS '''
        try:
            self.products = self.api.get_products()
        except api.CheckoutException as e:
            print(e)
            return

        self.id_catalog = {str(p.id): p for p in self.products}
        self.name_catalog = {p.name: p for p in self.products}

        print(f'Loaded {len(self.products)} products.')

    def do_lsproducts(self, arg):
        '''
        Show the loaded products, optionally in a given category: LSPRODUCTS [cat]
        '''
        if not arg:
            ps = self.products

        else:
            ps = [p for p in self.products if p.category == arg]

        for p in ps:
            print(p) # Todo prettyprinten

    def do_add(self, arg):
        '''
        Add a product to the cart, optionally multiple times: ADD product_id [...]
        '''

        ids = arg.split()

        for pid in ids:
            if pid in self.id_catalog:
                product = self.id_catalog[pid]
                print(f'Adding to cart: {product}')
                self.cart.append(product)

            elif pid in self.name_catalog:
                product = self.name_catalog[pid]
                print(f'Adding to cart: {product}')
                self.cart.append(product)

            else:
                print(f'Unknown product: {pid}')

    def do_clearcart(self, arg):
        ''' Clear the current cart: CLEARCART '''
        self.cart = []
        print('Your cart is now empty.')

    def do_checkout(self, arg):
        '''
        Attempt to finalize the purchase of the products in the cart: CHECKOUT
        '''
        try:
            result = self.user.purchase(self.cart)
        except api.CheckoutException as e:
            print(e)
            return

        print('Purchase successful! Ka-$hing!')
        self.do_clearcart('')

    def do_login(self, arg):
        '''
        Attempt to retrieve user information based on a card ID: LOGIN card_id
        '''
        user = self.api.get_card(arg)
        self.user = user

        print(f'Logged in as {user.first_name}, balance: {user.balance}')

    def do_logout(self, arg):
        ''' Clear 'current user' information, if present: LOGOUT '''
        self.user = None
        print('User information cleared.')

    def do_register(self, arg):
        '''
        Send a registration request for a new card: REGISTER card_id student_id
        '''
        args = arg.split()

        if len(args) != 2:
            print('Missing or too many arguments.')
            return

        self.api.create_card(*args)

    def do_token(self, arg):
        ''' Change the currently used token: TOKEN token '''
        if arg:
            self.api.token = arg
            print('Updated token.')
        else:
            print('You must specify a new token!')

    def do_server(self, arg):
        '''
        Show or change the currently used Koala instance: SERVER [server]
        '''
        args = arg.split()

        if args:
            server = args[0]
            self.api.server = server
            print(f'Set new server to {server}')

        else:
            print(f'Current server: {self.api.server}')

    def do_status(self, arg):
        ''' Show the current status: STATUS '''
        if self.products:
            print(f'{len(self.products)} products loaded.')
        else:
            print('No products loaded.')

        if self.user:
            print(f'Logged in as user: {self.user.first_name}, balance {self.user.balance}')
        else:
            print('Not logged in.')

        if self.cart:
            print()
            price = sum([p.price for p in self.cart])

            print(f'Cart: ({price})')
            for p in self.cart:
                print(f'- {p.name} ({p.price})')

    def do_EOF(self, arg):
        return self.do_exit(arg)

    def do_exit(self, arg):
        ''' Exit the shell: EXIT '''
        print('Bye!')
        return True

    def preloop(self):
        ''' Do setup and the needful. '''
        server = None
        token = None

        # Read .fakeoutrc if exists
        rcpath = os.path.expanduser('~/.fakeoutrc')
        if os.path.exists(rcpath):
            print('Using ~/.fakeoutrc')

            config = configparser.ConfigParser()
            config.read(rcpath)

            server = config['DEFAULT'].get('server', None)
            token = config['DEFAULT'].get('token', None)

        self.api = api.CheckoutApi(token, server)
        self.products = []
        self.cart = []
        self.user = None

        if self.api.server and self.api.token:
            self.do_getproducts('')

def main():
    FakeoutShell().cmdloop()

if __name__ == '__main__':
    main()
