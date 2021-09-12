import argparse
from dataclasses import dataclass
from typing import Any

from aioredis.pool import ConnectionsPool

from db import Database


@dataclass
class State:
    redis: ConnectionsPool = None
    db: Database = None


def mail_conversion(mail_dict):
    failed = [v for k, v in mail_dict["phones"].items() if v == "failed"]
    delivered = [v for k, v in mail_dict["phones"].items() if v == "delivered"]
    return {
        "timestamp": mail_dict["created_at"],
        "SMSText": mail_dict["text"],
        "mailingId": str(mail_dict["sms_id"]),
        "totalSMSAmount": mail_dict["phones_count"],
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
