# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import asyncio
import time
from datetime import timedelta
import logging
import ccxt

from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session
from datetime import datetime

# Bittensor
import bittensor as bt

import template
import os

# import base validator class which takes care of most of the boilerplate
from template.base.validator import BaseValidatorNeuron

# Bittensor Validator Template:
from template.validator import crud
from template.validator.database import SessionLocal, engine
from template.validator.db.models import Base
from template.validator.schemas import (
    Miner,
    Arbitrage,
)

DATABASE_URL = "sqlite:///example.db"
database_path = DATABASE_URL.split("sqlite///")[-1]

if not os.path.exists(database_path):
    Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_prices(exchange_id, symbol):
    price = None
    fees = 0.002  # Default fee value

    try:
        # Initialize the exchange
        exchange = getattr(ccxt, exchange_id)()

        # Load markets to ensure the exchange is ready
        exchange.load_markets()  # Ensure markets are loaded

        # Fetch the ticker price
        ticker = exchange.fetch_ticker(symbol)
        price = ticker["last"]

        # Fetch trading fees if available
        if exchange.has["fetchTradingFees"]:
            trading_fees = exchange.fetch_trading_fees()
            fees = trading_fees[symbol]["maker"]

    except (ccxt.NetworkError, ccxt.ExchangeError) as e:
        logger.error(
            f"Error fetching price or fees from {exchange_id} for {symbol}: {e}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    logger.info(
        f"The price and fees of {symbol} on {exchange_id} is {price} and {fees}"
    )

    return {"price": price, "fees": fees}


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()

        # TODO(developer): Anything specific to your use case you can do here

    async def forward(self, synapse: template.protocol.ArbitrageData):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        # TODO(developer): Rewrite this function based on your protocol definition.
        pass

    def run_transaction(
        self,
        synapse,
        miner_hotkey,
        amount_for_buying,
        fees1,
        fees2,
        price1,
        price2,
    ):
        # This function runs the transaction logic in a separate thread
        try:
            miner_db = crud.miner.get_miner(db=db, miner_hotkey=miner_hotkey)
            if not miner_db:
                # Handle creating a new miner
                # (Same logic as before)
                pass

            time.sleep(300)  # Simulating transaction time (5 minutes)

            # Update for Selling
            crud.miner.update(
                db=db,
                db_obj=miner_db,
                obj_in=Miner(
                    miner_hotkey=miner_hotkey,
                    last_updated=(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                    last_amount=miner_db.last_amount
                    + amount_for_buying * (1 - fees1) * price2 * (1 - fees2) / price1,
                    transaction_count=miner_db.transaction_count + 1,
                ),
            )

            # Create arbitrage entry
            crud.arbitrage.create(
                db=db,
                obj_in=Arbitrage(
                    miner_hotkey=miner_hotkey,
                    pair=synapse.pair,
                    exchange_from=synapse.exchange1,
                    exchange_to=synapse.exchange2,
                    price_from=price1,
                    price_to=price2,
                    fees_from=fees1,
                    fees_to=fees2,
                    amount=amount_for_buying,
                    timestamp=(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                    profit=(1 - fees1) * price2 * (1 - fees2) / price1 - 1,
                ),
            )

            logger.info(f"Transaction completed for miner {miner_hotkey}")

        except Exception as e:
            logger.error(f"Error during transaction for {miner_hotkey}: {e}")

    async def forward_arbitrage(
        self, synapse: template.protocol.ArbitrageData
    ) -> template.protocol.ArbitrageData:
        """
        Processes the incoming 'ArbitrageData' synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (template.protocol.ArbitrageData): The synapse object containing the 'dummy_input' data.

        Returns:
            template.protocol.ArbitrageData: The synapse object with the 'dummy_output' field set to twice the 'dummy_input' value.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """
        # TODO(developer): Replace with actual implementation logic.
        try:
            miner_hotkey = synapse.dendrite.hotkey

            if synapse.amount > 1 or synapse.amount < 0:
                synapse.message = "Amount percentage must be between 0 and 1"
                synapse.status_code = 404
                synapse.after_amount = synapse.amount

                return synapse

            data1 = await fetch_prices(synapse.exchange1, synapse.pair.upper())
            data2 = await fetch_prices(synapse.exchange2, synapse.pair.upper())
            price1 = data1["price"]
            price2 = data2["price"]
            fees1 = data1["fees"]
            fees2 = data2["fees"]
            if price1 is None or price2 is None:
                print("Error fetching prices")
                synapse.message = "Error fetching prices"
                synapse.status_code = 404
                synapse.after_amount = synapse.amount

                return synapse

            miner_db = crud.miner.get_miner(db=db, miner_hotkey=miner_hotkey)

            # if there is no miner data then create a new one
            if not miner_db:
                # Create new miner entry
                crud.miner.create(
                    db=db,
                    obj_in=Miner(
                        miner_hotkey=miner_hotkey,
                        last_updated=(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                        last_amount=10000,
                        transaction_count=0,
                    ),
                )

                print(f"Created new miner entry for miner_hotkey: {miner_hotkey}")

                miner_db = crud.miner.get_miner(db=db, miner_hotkey=miner_hotkey)
                last_amount = miner_db.last_amount

                # Update for Buying transaction
                crud.miner.update(
                    db=db,
                    db_obj=miner_db,
                    obj_in=Miner(
                        miner_hotkey=miner_hotkey,
                        last_updated=(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                        last_amount=last_amount
                        - last_amount * synapse.amount * (1 + fees1),
                        transaction_count=miner_db.transaction_count,
                    ),
                )

                amount_for_buying = (last_amount) * (synapse.amount)
                synapse.message = "Data updated successfully"
                synapse.status_code = 200
                synapse.after_amount = (
                    last_amount
                    + amount_for_buying * (1 - fees1) * price2 * (1 - fees2) / price1
                )

                # Use TreadPoolExecutor to run the transaction in a separate thread
                # with ThreadPoolExecutor() as executor:
                #     executor.submit(
                #         self.run_transaction,
                #         synapse,
                #         miner_hotkey,
                #         amount_for_buying,
                #         fees1,
                #         fees2,
                #         price1,
                #         price2,
                #     )

                with ThreadPoolExecutor() as executor:
                    await asyncio.get_event_loop().run_in_executor(
                        executor,
                        self.run_transaction,
                        synapse,
                        miner_hotkey,
                        amount_for_buying,
                        fees1,
                        fees2,
                        price1,
                        price2,
                    )

                return synapse

            # If there is miner data then update the data

            # If the current amount is 0 then return error
            if miner_db.last_amount <= 0:
                print("Amount is greater than current amount")
                synapse.message = "Your amount is not sufficient to operate arbitrage"
                synapse.status_code = 404
                synapse.after_amount = False
                return synapse

            amount_for_buying = (miner_db.last_amount) * (synapse.amount)
            last_amount = miner_db.last_amount
            # Update for Buying transaction
            crud.miner.update(
                db=db,
                db_obj=miner_db,
                obj_in=Miner(
                    miner_hotkey=miner_db.miner_hotkey,
                    last_updated=(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                    last_amount=last_amount - amount_for_buying * (1 + fees1),
                    transaction_count=miner_db.transaction_count,
                ),
            )

            synapse.message = "Data updated successfully"
            synapse.status_code = 200
            synapse.after_amount = (
                last_amount
                + amount_for_buying * (1 - fees1) * price2 * (1 - fees2) / price1
            )
            # Use TreadPoolExecutor to run the transaction in a separate thread
            # with ThreadPoolExecutor() as executor:
            #     executor.submit(
            #         self.run_transaction,
            #         synapse,
            #         miner_hotkey,
            #         amount_for_buying,
            #         fees1,
            #         fees2,
            #         price1,
            #         price2,
            #     )

            with ThreadPoolExecutor() as executor:
                await asyncio.get_event_loop().run_in_executor(
                    executor,
                    self.run_transaction,
                    synapse,
                    miner_hotkey,
                    amount_for_buying,
                    fees1,
                    fees2,
                    price1,
                    price2,
                )

            return synapse

        except Exception as e:
            print(e)
            raise e


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(5)
