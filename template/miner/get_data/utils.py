import asyncio
import requests
from datetime import datetime, timedelta

def get_usdt_pairs():
    # Get exchanges data from CoinPaprika
    exchanges_url = "https://api.coinpaprika.com/v1/exchanges"
    # exchanges_url1 = "https://api.coingecko.com/api/v3"
    exchanges_response = requests.get(exchanges_url)

    if exchanges_response.status_code != 200:
        print("Error fetching exchanges data")
        return

    exchanges = exchanges_response.json()

    # Filter out exchanges that are not active, have no website, or no API
    filtered_exchanges = [
        exchange
        for exchange in exchanges
        if (exchange["reported_rank"] is not None)
        and exchange["active"]
        and exchange["website_status"]
        and exchange["api_status"]
    ]

    sorted_exchanges = sorted(filtered_exchanges, key=lambda x: x["adjusted_rank"])

    usdt_pairs = []

    count = 0
    # Iterate through each exchange to get its markets
    for exchange in sorted_exchanges:
        """Giving limitation to 60 requests per hour"""
        # Get markets for the 15 exchange
        if count > 14:
            break

        count += 1

        if count > 10:

            markets_url = (
                f"https://api.coinpaprika.com/v1/exchanges/{exchange['id']}/markets"
            )
            markets_response = requests.get(markets_url)

            if markets_response.status_code != 200:
                print(f"Error fetching markets for {exchange['name']}")
                continue

            markets = markets_response.json()

            # Filter for pairs that include USDT
            for market in markets:
                # Check if the market contains USDT and the last_updated is within the last 10 minutes
                if (
                    ("/USDT" in market["pair"])
                    # and (
                    #     (
                    #         datetime.now()
                    #         - datetime.fromisoformat(market["last_updated"][:-1])
                    #         + timedelta(hours=5)
                    #     ).total_seconds()
                    #     < 600
                    # )
                    and market["market_url"]
                ):
                    usdt_pairs.append(
                        {
                            "exchange": exchange["id"],
                            "pair": market["pair"],
                            "currency_name": market["base_currency_name"],
                            "currency_id": market["base_currency_id"],
                            "outlier": market["outlier"],
                            "price": market["quotes"]["USD"][
                                "price"
                            ],  # Adjust based on available fields
                            "volume": market["quotes"]["USD"]["volume_24h"]
                            / market["quotes"]["USD"][
                                "price"
                            ],  # Adjust based on available fields
                            "timestamp": datetime.fromisoformat(
                                market["last_updated"][:-1]
                            ),  # Convert to datetime
                        }
                    )

    return usdt_pairs


def usdt_pairs():
    Currency_data = get_usdt_pairs()

    # Check if data is valid
    if Currency_data is None:
        return None

    # Use a dictionary to group exchanges by pair
    pairs_dict = {}
    for data in Currency_data:
        if data["volume"] != 0:
            pair = data["pair"]
            if pair not in pairs_dict:
                pairs_dict[pair] = []
            pairs_dict[pair].append(data)

    db_pairs = []

    # Process pairs in the grouped dictionary
    for pair, exchanges in pairs_dict.items():
        if len(exchanges) < 2:
            continue

        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                ex1 = exchanges[i]
                ex2 = exchanges[j]
                if (
                    ex1["exchange"] != ex2["exchange"]
                    and ex1["price"] != ex2["price"]
                    and ex1["currency_id"] == ex2["currency_id"]
                    and (ex1["outlier"] or ex2["outlier"])
                ):
                    price_from = min(ex1["price"], ex2["price"])
                    price_to = max(ex1["price"], ex2["price"])
                    profit = 100 * (price_to / price_from) - 100

                    # Filter based on the given condition
                    if 101 < (price_to / price_from) * 100 < 1000:
                        item = {
                            "pair": pair + "(" + ex1["currency_name"] + ")",
                            "exchange_from": (
                                ex1["exchange"]
                                if ex1["price"] < ex2["price"]
                                else ex2["exchange"]
                            ),
                            "exchange_to": (
                                ex2["exchange"]
                                if ex1["price"] < ex2["price"]
                                else ex1["exchange"]
                            ),
                            "price_from": price_from,
                            "price_to": price_to,
                            "volume": (
                                ex1["volume"]
                                if ex1["price"] > ex2["price"]
                                else ex2["volume"]
                            ),
                            "profit": profit,
                            "time_from": max(ex1["timestamp"], ex2["timestamp"]),
                            "price_ratio": (price_to / price_from)
                            * 100,  # Calculate price ratio for sorting
                        }
                        db_pairs.append(item)

    # Sort db_pairs by price ratio in ascending order
    sorted_db_pairs = sorted(db_pairs, key=lambda x: x["price_ratio"])

    return sorted_db_pairs