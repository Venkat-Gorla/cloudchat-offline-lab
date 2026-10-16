import argparse
import httpx2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["send", "inbox"])
    parser.add_argument("--user", required=True)
    parser.add_argument("--server", default="http://127.0.0.1:8000")
    parser.add_argument("--to")
    parser.add_argument("--message")
    args = parser.parse_args()

    headers = {"X-User-ID": args.user}

    with httpx2.Client(base_url=args.server, timeout=5.0) as client:
        if args.command == "send":
            if not args.to or not args.message:
                parser.error("send requires --to and --message")

            response = client.post(
                "/messages",
                headers=headers,
                json={"recipient": args.to, "body": args.message},
            )
            response.raise_for_status()
            print(response.json())

        else:
            response = client.get("/messages", headers=headers)
            response.raise_for_status()

            for message in response.json()["messages"]:
                print(
                    f'#{message["id"]} '
                    f'{message["sender"]} → {message["recipient"]}: '
                    f'{message["body"]}'
                )


if __name__ == "__main__":
    main()
