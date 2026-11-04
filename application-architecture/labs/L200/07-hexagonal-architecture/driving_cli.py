"""Driving adapter: command line -> ForManagingLoans. Translates domain errors to exit codes.

Run on its own (persists in a SQLite file):
    python driving_cli.py --db library.db borrow b1 m1
    python driving_cli.py --db library.db return 1
"""
import argparse
import json
import sys

from domain import LoanError, LoanNotFound

EXIT = {LoanNotFound: 3}  # any other rule violation -> 2, bad input -> 1


def run_cli(argv, loans, out=sys.stdout):
    parser = argparse.ArgumentParser(prog="loans")
    sub = parser.add_subparsers(dest="command", required=True)
    borrow = sub.add_parser("borrow")
    borrow.add_argument("book_id")
    borrow.add_argument("member_id")
    sub.add_parser("return").add_argument("loan_id", type=int)
    sub.add_parser("show").add_argument("loan_id", type=int)
    args = parser.parse_args(argv)
    try:
        if args.command == "borrow":
            loan = loans.borrow(args.book_id, args.member_id)
        elif args.command == "return":
            loan = loans.give_back(args.loan_id)
        else:
            loan = loans.get(args.loan_id)
    except (LoanError, ValueError) as exc:
        print(f"error: {exc}", file=out)
        return EXIT.get(type(exc), 2 if isinstance(exc, LoanError) else 1)
    print(json.dumps({"id": loan.id, "bookId": loan.book_id, "memberId": loan.member_id,
                      "status": "returned" if loan.returned else "active"}), file=out)
    return 0


if __name__ == "__main__":
    from app import build  # composition root picks the driven adapter

    top = argparse.ArgumentParser(add_help=False)
    top.add_argument("--db", default="library.db")
    known, rest = top.parse_known_args()
    sys.exit(run_cli(rest, build("sqlite", known.db)))
