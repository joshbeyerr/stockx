from stockxm import StockX


def save_tokens(access, refresh):
    with open('../stockx_main/tokens', 'w') as f:
        f.write(test.access_token)
        f.write('\n')
        f.write(test.refresh_token)


def read_tokens():
    with open('../stockx_main/tokens', 'r') as f:
        access = f.readline()
        refresh = f.readline()
        return {'access': access.strip('\n'), 'refresh': refresh.strip('\n')}


test = StockX('ZoUZKVD8W42uY5wi5kzuP5AuNfAi5gKX758JIA2Y', 'ECb52FQVCrdpJwc1kWd1R8pV7HJUHyfk',
              'Vl4LC0EEoLvzqOXFaKFOvOqv-DUpMVB5K-wtLBKiUBYjMCdfmxMXtrPcaxhNqPym')

# test.auth()
# save_tokens(test.access_token, test.refresh_token)
# quit()


tokens = read_tokens()
test.set_refresh(tokens['refresh'])
test.set_access(tokens['access'])


# set tokens, if not test.auth()

# create session which stores auth tokens in headers

test.create_session()

# retrieve and set with refresh token
def refresh_token():
    test.set_access(test.refresh().json()['access_token'])
    save_tokens(test.access_token, test.refresh_token)
    tokens = read_tokens()
    test.set_refresh(tokens['refresh'])
    test.set_access(tokens['access'])

# refresh_token()


def market_by_sku(sku):
    try:
        searching = test.search(sku).json()

        if searching['products'][0]['styleId'] == sku:
            print('Found Product')
        else:
            print('Sku Not on StockX')
    except KeyError:
        print('Need New Token')
        quit()

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



market_by_sku('1122553-MDSD')