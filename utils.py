import argparse
from dataclasses import dataclass

import aioredis.connection as con
from pydantic import BaseModel, BaseSettings, ConstrainedStr

from db import Database


@dataclass
class State:
    redis: con.ConnectionPool = None
    db: Database = None


def transform_mailing(status_dict):
    failed = [v for k, v in status_dict["phones"].items() if v == "failed"]
    delivered = [
        v for k, v in status_dict["phones"].items() if v == "delivered"
    ]
    return {
        "timestamp": status_dict["created_at"],
        "SMSText": status_dict["text"],
        "mailingId": str(status_dict["sms_id"]),
        "totalSMSAmount": status_dict["phones_count"],
        "deliveredSMSAmount": len(delivered),
        "failedSMSAmount": len(failed),
    }


def create_argparser():
    parser = argparse.ArgumentParser(
        description="Redis database usage example"
    )
    parser.add_argument(
        "--address",
        default="redis://localhost:6379",
        action="store",
        dest="redis_uri",
        help="Redis URI",
    )
    parser.add_argument(
        "--password",
        action="store",
        dest="redis_password",
        help="Redis db password",
    )
    return parser


class Message(ConstrainedStr):
    min_length = 1


class Mailing(BaseModel):
    message: Message


class Settings(BaseSettings):
    login: str
    password: str
