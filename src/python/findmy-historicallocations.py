import asyncio
import json
import logging
from pathlib import Path
import os
import csv
import datetime
import json

from findmy import KeyPair
from findmy.reports import (
    AsyncAppleAccount,
    LoginState,
    RemoteAnisetteProvider,
    SmsSecondFactorMethod,
    TrustedDeviceSecondFactorMethod
)

# URL to (public or local) anisette server
ANISETTE_SERVER = "http://localhost:6969"

# Apple account details
ACCOUNT_EMAIL = ""
ACCOUNT_PASS = ""

logging.basicConfig(level=logging.DEBUG)


async def login(account: AsyncAppleAccount) -> None:
    state = await account.login(ACCOUNT_EMAIL, ACCOUNT_PASS)

    if state == LoginState.REQUIRE_2FA:  # Account requires 2FA
        # This only supports SMS methods for now
        methods = await account.get_2fa_methods()

        # Print the (masked) phone numbers
        for i, method in enumerate(methods):
            if isinstance(method, TrustedDeviceSecondFactorMethod):
                print(f"{i} - Trusted Device")
            elif isinstance(method, SmsSecondFactorMethod):
                print(f"{i} - SMS ({method.phone_number})")

        ind = int(input("Method? > "))

        method = methods[ind]
        await method.request()
        code = input("Code? > ")

        # This automatically finishes the post-2FA login flow
        await method.submit(code)

# Define a custom function to serialize datetime objects 
def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 

async def fetch_reports(keys: list[KeyPair]) -> None:
    anisette = RemoteAnisetteProvider(ANISETTE_SERVER)
    acc = AsyncAppleAccount(anisette)

    try:
        acc_store = Path("account.json")
        try:
            with acc_store.open() as f:
                acc.restore(json.load(f))
        except FileNotFoundError:
            await login(acc)
            with acc_store.open("w+") as f:
                json.dump(acc.export(), f)

        print(f"Logged in as: {acc.account_name} ({acc.first_name} {acc.last_name})")

        # It's that simple!
        reports = await acc.fetch_last_reports(keys)

        dump_list = []
        for keypair in reports:
            report = reports[keypair]
            for r in report:
                obj = {
                    "time": r.timestamp,
                    "lat": r.latitude,
                    "lon": r.longitude,
                    "published_at": r.published_at,
                    "description": r.description,
                    "confidence": r.confidence,
                    "status": r.status,
                    "key": r.key.private_key_b64
                }
                dump_list.append(obj)

        json_object = json.dumps(dump_list, indent=4, default=serialize_datetime)

        with open("location_history.json", "w") as outfile:
            outfile.write(json_object)

    finally:
        await acc.close()


if __name__ == "__main__":
    file = open('discovery-keys.csv', "r")
    csvreader = csv.reader(file, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')
    private_keys = []
    for row in csvreader:
        private_keys.append(KeyPair.from_b64(row[2]))
    file.close()

    asyncio.run(fetch_reports(private_keys))