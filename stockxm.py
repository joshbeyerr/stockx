import requests
import webbrowser


class StockX:
    def __init__(self, apikey, clientid, clientsecret):
        self.api_key = apikey
        self.client_id = clientid
        self.client_secret = clientsecret
        self.access_token = None  # Initialize as None
        self.refresh_token = None
        self.currency = "CAD"
        self.session = None

    def auth(self):
        s = requests.session()
        auth_url = "https://accounts.stockx.com/authorize"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": "https://stockx.com/",
            "scope": "offline_access openid",
            "audience": "gateway.stockx.com",
            "state": "abcXYZ9876"
        }

        auth_url = requests.Request('GET', auth_url, params=params).prepare().url
        webbrowser.open(auth_url)

        s.headers.update({
            "content-type": "application/x-www-form-urlencoded"
        })

        code = input('Enter the URL that you were redirected to after authorizing the application: ')

        loginData = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': 'https://stockx.com',

        }

        tokens = (s.post("https://accounts.stockx.com/oauth/token", data=loginData)).json()
        self.access_token = tokens.get("access_token")
        self.refresh_token = tokens.get("refresh_token")

    def set_access(self, accessToken):
        self.access_token = accessToken

    def set_refresh(self, refreshToken):
        self.refresh_token = refreshToken

    def set_currency(self, currency):
        self.currency = currency

    def create_session(self):
        s = requests.session()
        s.headers.update({
            'Authorization': 'Bearer {}'.format(self.access_token),
            'x-api-key': self.api_key
        })
        self.session = s

    def refresh(self):
        refreshData = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': 'gateway.stockx.com',
            'refresh_token': self.refresh_token
        }
        return self.session.post("https://accounts.stockx.com/oauth/token", data=refreshData)

    # batch
    def create_batch_listings(self, items):
        return self.session.post('https://api.stockx.com/v2/selling/batch/create-listing', data=items)

    def get_batch_status(self, batchId):
        return self.session.get('https://api.stockx.com/v2/selling/batch/create-listing/{}'.format(batchId))

    def get_batch_items(self, batchId, status=None):
        if status:
            return self.session.get(
                'https://api.stockx.com/v2/selling/batch/create-listing/{}/items?status={}'.format(batchId), status)
        else:
            return self.session.get('https://api.stockx.com/v2/selling/batch/create-listing/{}/items'.format(batchId))

    def delete_batch_listings(self, items):
        return self.session.post('https://api.stockx.com/v2/selling/batch/delete-listing', data=items)

    def get_deleted_status(self, batchId):
        return self.session.get('https://api.stockx.com/v2/selling/batch/delete-listing/{}'.format(batchId))

    def get_deleted_items(self, batchId, status=None):
        if status:
            return self.session.get(
                'https://api.stockx.com/v2/selling/batch/delete-listing/{}/items?status={}'.format(batchId), status)
        else:
            return self.session.get('https://api.stockx.com/v2/selling/batch/delete-listing/{}/items'.format(batchId))

    # listings
    def create_listing(self, amount, variant):
        return self.session.post('https://api.stockx.com/v2/selling/listings', data={
            "amount": amount,
            "variantId": variant,
            "currencyCode": self.currency,
        })

    def get_listings(self, pageNumber=1, pageSize=1, listingStatuses="ACTIVE"):
        return self.session.get(
            'https://api.stockx.com/v2/selling/listings?pageNumber={}&pageSize={}&{}'.format(pageNumber, pageSize,
                                                                                             listingStatuses))

    def search_prod(self, product_id):
        return self.session.get('https://api.stockx.com/v2/catalog/products/{}'.format(product_id))

    def search_prod_variant(self, product_id, variant_id):
        return self.session.get(
            'https://api.stockx.com/v2/catalog/products/{}/variants/{}'.format(product_id, variant_id))

    def get_variants(self, product_id):
        return self.session.get('https://api.stockx.com/v2/catalog/products/{}/variants'.format(product_id))

    def get_market(self, product_id, variant_id):
        return self.session.get(
            'https://api.stockx.com/v2/catalog/products/{}/variants/{}/market-data?currencyCode={}'.format(product_id,
                                                                                                           variant_id,
                                                                                                           self.currency))

    def search(self, search_term, pageSize=1, pageNum=1):
        return self.session.get(
            'https://api.stockx.com/v2/catalog/search?query={}&pageNumber={}&pageSize={}'.format(search_term, pageNum,
                                                                                                 pageSize))

    # max of 20 threads created
    def mass_get_market(self, prodID, input_list):
        returnList = []

        def process_list(input_list2):
            # Replace this function with your custom processing logic for each thread
            for item in input_list2:
                returnList.append(self.get_market(prodID, item).json())

        import threading

        # Calculate the number of threads needed based on the maximum of 20 threads
        num_threads = min(len(input_list), 20)

        # Calculate the number of elements to assign to each thread
        chunk_size = len(input_list) // num_threads
        remainder = len(input_list) % num_threads

        # Create a list to store the threads
        threads = []

        # Create and start threads
        for i in range(num_threads):
            start_index = i * chunk_size
            end_index = start_index + chunk_size + (1 if i < remainder else 0)
            thread_list = input_list[start_index:end_index]
            thread = threading.Thread(target=process_list, args=(thread_list,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return returnList


# usage


def save_tokens(access, refresh):
    with open('../stockx_python_wrapper/tokens', 'w') as f:
        f.write(test.access_token)
        f.write('\n')
        f.write(test.refresh_token)


def read_tokens():
    with open('../stockx_python_wrapper/tokens', 'r') as f:
        access = f.readline()
        refresh = f.readline()
        return {'access': access.strip('\n'), 'refresh': refresh.strip('\n')}




# create StockX object
test = StockX('ZoUZKVD8W42uY5wi5kzuP5AuNfAi5gKX758JIA2Y', 'ECb52FQVCrdpJwc1kWd1R8pV7HJUHyfk',
              'Vl4LC0EEoLvzqOXFaKFOvOqv-DUpMVB5K-wtLBKiUBYjMCdfmxMXtrPcaxhNqPym')

# test.auth()
# save_tokens(test.access_token, test.refresh_token)
tokens = read_tokens()
test.set_access(tokens['access'])
test.set_refresh(tokens['refresh'])

# set tokens, if not test.auth()

# create session which stores auth tokens in headers
test.create_session()


def market_by_sku(sku):
    searching = test.search(sku).json()
    if searching['products'][0]['styleId'] == sku:
        print('Found Product')
    else:
        print('Sku Not on StockX')

    getVars = (test.get_variants(searching['products'][0]['productId'])).json()
    varList = []
    for x in getVars:
        varList.append(x['variantId'])

    marketAll = test.mass_get_market(searching['products'][0]['productId'], varList)

    final = []

    for x, y in zip(getVars, marketAll):
        x.update(y)
        final.append(x)

    print(final)


market_by_sku('HQ4207')
# prod3 = (test.get_variants('34fcdb59-9c42-4f29-bb66-b5235396880c')).json()
#
# print(prod3)
# vars = []
#
# for x in prod3:
#     market = test.get_market(x['productId'], x['variantId'])
#     print('Size {}'.format(x['variantValue']))
#     print(market.text)
#     vars.append(x['variantId'])
#
# print(vars)