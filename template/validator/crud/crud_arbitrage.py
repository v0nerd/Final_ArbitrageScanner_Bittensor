from template.validator.crud.base import CRUDBase
from template.validator.db.models import Arbitrage

from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import update, delete, tuple_
from template.validator.schemas.arbitrage import ArbitrageCreate, ArbitrageUpdate
import asyncio
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text


class CRUDArbitrage(CRUDBase[Arbitrage, ArbitrageCreate, ArbitrageUpdate]):
    def get_arbitrages(self, db: Session, *, miner_hotkey: str) -> Optional[Arbitrage]:
        return (
            db.query(Arbitrage)
            .filter(
                Arbitrage.miner_hotkey == miner_hotkey,
            ).all()
        )

    def get_data(self, db: Session):
        result = db.query(Arbitrage).all()
        return result

    def update(
        self,
        db: Session,
        *,
        db_obj: Arbitrage,
        obj_in: Union[ArbitrageUpdate, Dict[str, Any]],
    ) -> Arbitrage:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    async def batch_update(
        self, db: Session, *, update_values: List[Dict[str, Any]], batch_size: int = 100
    ) -> None:
        try:
            # Get all current records in the database
            db.execute(text("PRAGMA journal_mode=WAL;"))

            update_identifiers = set(
                (record["pair"], record["exchange_from"], record["exchange_to"])
                for record in update_values
            )

            existing_ids = set(
                db.query(Arbitrage.pair, Arbitrage.exchange_from, Arbitrage.exchange_to).all()
            )

            # Delete records not in update_values
            delete_ids = existing_ids - update_identifiers
            if delete_ids:
                db.query(Arbitrage).filter(
                    tuple_(Arbitrage.pair, Arbitrage.exchange_from, Arbitrage.exchange_to).in_(
                        delete_ids
                    )
                ).delete(synchronize_session=False)
                db.commit()

            # Proceed with the batch update/insert process
            for i in range(0, len(update_values), batch_size):
                batch = update_values[i : i + batch_size]

                for record in batch:
                    stmt = (
                        insert(Arbitrage)
                        .values(
                            pair=record["pair"],
                            exchange_from=record["exchange_from"],
                            exchange_to=record["exchange_to"],
                            price_from=record.get("price_from"),
                            price_to=record.get("price_to"),
                            fees_from=record.get("fees_from"),
                            fees_to=record.get("fees_to"),
                            volume=record.get("volume"),
                            profit=record.get("profit"),
                            time_from=(record.get("time_from")).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        )
                        .on_conflict_do_update(
                            index_elements=["pair", "exchange_from", "exchange_to"],
                            set_={
                                "price_from": record.get("price_from"),
                                "price_to": record.get("price_to"),
                                "volume": record.get("volume"),
                                "profit": record.get("profit"),
                                # Update other fields as necessary
                            },
                        )
                    )

                    # Execute the UPSERT statement
                    db.execute(stmt)

                db.commit()

        except Exception as e:
            db.rollback()
            raise e


arbitrage = CRUDArbitrage(Arbitrage)
