import argparse
import os

import requests

SPLUNKBASE_BASE_URL = "https://splunkbase.splunk.com/api/v1"


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--appid", help="App ID", required=True)
    parser.add_argument("-v", "--version", help="SplunkVersion", default="8.0,8.1,8.2")
    parser.add_argument("-c", "--cimversion", help="CIMVersion")
    parser.add_argument("-f", "--file", help="Files", required=True)
    parser.add_argument("-w", "--visibility", help="Visibility", default="false")
    return parser


def release(args: argparse.Namespace):
    files = {
        "files[]": open(os.path.basename(args.file), "rb"),
    }
    data = {
        "filename": os.path.basename(args.file),
        "splunk_versions": args.version,
        "visibility": args.visibility,
    }
    if args.cimversion:
        files["cim_versions"] = args.cimversion

    user = os.getenv("SPLUNK_USERNAME")
    password = os.getenv("SPLUNK_PASSWORD")

    auth = (user, password)
    if not all(auth):
        raise Exception("Missing credentials")

    res = requests.post(
        f"{SPLUNKBASE_BASE_URL}/app/{args.appid}/new_release/",
        data=data,
        files=files,
        auth=auth,
    )
    res.raise_for_status()

    package_id = res.json()["id"]
    print(f"Release created: {package_id}")

    res = requests.get(f"{SPLUNKBASE_BASE_URL}/package/{package_id}/", auth=auth)
    res.raise_for_status()

    package_status = res.json()
    package_result = package_status["result"]
    package_message = package_status["message"]
    print(f"Package status: {package_result}")
    print(f"Package message: {package_message}")

    if package_result == "fail":
        raise Exception(package_message)


def main():
    parser = get_parser()
    args = parser.parse_args()
    release(args)


if __name__ == "__main__":
    main()
