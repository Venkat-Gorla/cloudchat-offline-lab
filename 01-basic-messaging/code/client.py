"""
- Send a message:
uv run code/client.py send --user alice --to bob --message "Hello Bob"

- Retrieve Bob's inbox:
uv run code/client.py inbox --user bob
"""

import argparse
import httpx2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["send", "inbox"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--server", default="http://127.0.0.1:8000")
    parser.add_argument("--to")
    parser.add_argument("--message")

    return parser.parse_args()


def send_message(client, headers, args):
    if not args.to or not args.message:
        raise ValueError("send requires --to and --message")

    response = client.post(
        "/messages",
        headers=headers,
        json={"recipient": args.to, "body": args.message},
    )
    response.raise_for_status()
    print(response.json())


def get_inbox(client, headers):
    response = client.get("/messages", headers=headers)
    response.raise_for_status()
    return response.json()["messages"]


def print_inbox(messages):
    for message in messages:
        print(
            f'#{message["id"]} '
            f'{message["sender"]} → {message["recipient"]}: '
            f'{message["body"]}'
        )


def main():
    args = parse_args()
    headers = {"X-User-ID": args.user}

    with httpx2.Client(base_url=args.server, timeout=5.0) as client:
        if args.command == "send":
            send_message(client, headers, args)
        else:
            messages = get_inbox(client, headers)
            print_inbox(messages)


if __name__ == "__main__":
    main()
