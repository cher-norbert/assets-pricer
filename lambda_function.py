import json

from assetspricer.assetspricer import AssetsPricer


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    ap = AssetsPricer('./assets-pricer.ini')

    if 'instrument_id' in event:
        ap.insert_price_history(event['instrument_id'])

    else:
        ap.update_daily_prices()

    return
