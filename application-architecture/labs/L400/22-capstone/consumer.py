"""Consumer side of the contract (capstone): the member portal reads a member's loans.

Run: python consumer.py   writes contracts/member-portal--loans-service.json after the client passed against
the mock provider (lesson 14 flow, lesson-14 contract format; Pact is the equivalent in CI).
"""
import json
import pathlib
import urllib.request

from reuse import contract

HERE = pathlib.Path(__file__).resolve().parent
MEMBER = {"id": "m1", "tenant": "lib00", "roles": ["member"]}


def portal_loans(base_url, tenant, member, subject):
    """The portal's real client code: it reads memberId and each loan's bookId."""
    req = urllib.request.Request(f"{base_url}/tenants/{tenant}/members/{member}/loans",
                                 headers={"X-Subject": json.dumps(subject)})
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["memberId"], [loan["bookId"] for loan in body["loans"]]


def build():
    builder = contract.ContractBuilder("member-portal", "loans-service", "2.0.0").interaction(
        "a member reads their loans", "member m1 of lib00 has one loan", "GET", "/tenants/lib00/members/m1/loans",
        200, {"memberId": contract.like("m1"), "loans": contract.like([{"loanId": 1, "bookId": "b1"}])})
    # lesson-14 format has no eachLike: `loans` is type-matched as a list (its items are not checked)
    with builder.mock_provider() as url:  # the client must work against the declared response
        assert portal_loans(url, "lib00", "m1", MEMBER) == ("m1", ["b1"])
    return builder.write(HERE / "contracts")


if __name__ == "__main__":
    print(f"contract written: {build().relative_to(HERE).as_posix()}")
