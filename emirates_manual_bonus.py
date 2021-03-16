
from lcp_requests import *
from lcp_credentials import *


########################################################################################################################
def get_base_info(parent_order_url: str, cid: str):
    print("-------------- GETTING PARENT ORDER --------------")
    parent_order = lcp_request(user_mac_key_id, user_mac_key, 'GET', parent_order_url, cid=cid, print_rsp=False)
    try:
        base_info = {
            "lp": parent_order["data"]["loyaltyProgram"],
            "first_name": parent_order["data"]["user"].get("firstName"),
            "last_name": parent_order["data"]["user"].get("lastName"),
            "email": parent_order["data"]["user"].get("email"),
            "member_id": parent_order["data"]["user"].get("memberId"),
            "currency": parent_order["data"]["payment"].get("currency"),
            "base_points": parent_order["data"]["orderDetails"]["basePoints"]
        }
    except:
        base_info = {}
    return base_info


########################################################################################################################
def get_bonus_info(base_info: dict, offer_url: str, cid: str):
    bonus_info = {}
    print("-------------- GETTING BONUS OFFER --------------")
    offer = lcp_request(user_mac_key_id, user_mac_key, 'GET', offer_url, cid=cid, print_rsp=False)
    for tier in offer["feeSchedule"]["pricing"]["tiers"]:
        if tier["bonusAmount"] > 0 and tier["minOfRange"] <= base_info["base_points"] <= tier["maxOfRange"]:
            try:
                bonus_info["pic"] = tier["pics"]["bonus"]
            except:
                bonus_info["pic"] = ""
            if tier["bonusType"] == "percentage":
                bonus_info["amount"] = round(base_info["base_points"] * tier["bonusAmount"] * 0.01)
            for rate in tier["retailRates"]:
                if base_info["currency"] == rate["currency"]:
                    bonus_info["retailRate"] = rate["rate"]
    return bonus_info


########################################################################################################################
def create_mv(base_info: dict, cid: str):
    print("------------------ CREATING MV ------------------")
    url = base_info["lp"] + '/mvs/'
    req_body = {
        "identifyingFactors": {
            "memberId": base_info["member_id"],
            "lastName": base_info["last_name"]
        }
    }
    mv = lcp_request(app_mac_key_id, app_mac_key, 'POST', url, req_body, cid=cid, print_rsp=True)
    return mv


########################################################################################################################
def create_order(base_info: dict, mv: dict, bonus_info: dict, parent_order_url: str, offer_url: str, ticket: str,
                 cid: str):
    print("--------------- CREATING ORDER ---------------")
    url = base_info["lp"][:-41] + '/orders/'
    req_body = {
        "data": {
            "loyaltyProgram": base_info["lp"],
            "orderDetails": {
                "approvedBy": "see " + ticket,
                "bonusPoints": bonus_info["amount"],
                "createdBy": "see " + ticket,
                "memberValidationData": {
                    "application": mv["application"],
                    "balance": mv["balance"],
                    "email": base_info["email"],
                    "firstName": base_info["first_name"],
                    "lastName": base_info["last_name"],
                    "links": {
                        "self": {
                            "href": mv["links"]["self"]["href"]
                        }
                    },
                    "memberId": base_info["member_id"],
                    "status": "success"
                },
                "loyaltyProgram": base_info["lp"],
                "offer": offer_url,
                "pics": {},
                "ticket": ticket
            },
            "parentOrderId": parent_order_url,
            "payment": {},
            "user": {
                "balance": mv["balance"],
                "email": base_info["email"],
                "firstName": base_info["first_name"],
                "lastName": base_info["last_name"],
                "memberId": base_info["member_id"],
                "memberValidation": mv["links"]["self"]["href"]
            }
        },
        "orderType": "MANUAL_BONUS"
    }
    # Add optional properties to order request body
    if bonus_info.get("pic"):
        req_body["data"]["orderDetails"]["pics"]["bonus"] = bonus_info["pic"]
    if base_info.get("currency"):
        req_body["data"]["payment"]["currency"] = base_info["currency"]
    if bonus_info.get("retailRate"):
        req_body["data"]["orderDetails"]["retailRate"] = bonus_info["retailRate"]
    order = lcp_request(app_mac_key_id, app_mac_key, 'POST', url, req_body, cid=cid, print_rsp=True)
    return order


########################################################################################################################
def link_order_to_mv(mv_url: str, order_url: str, cid: str):
    print("------------ LINKING ORDER TO MV ------------")
    req_body = {
        "order": order_url
    }
    rsp = lcp_request(app_mac_key_id, app_mac_key, 'PATCH', mv_url, req_body, cid=cid, print_rsp=True)
    return rsp


########################################################################################################################
def create_credit(mv_url: str, amount: int, cid: str, pic=None):
    print("--------------- CREATING CREDIT ---------------")
    url = mv_url[:-41] + '/credits/'
    req_body = {
        "amount": amount,
        "memberValidation": mv_url,
        "creditType": "bonus"
    }
    if pic:
        req_body["pic"] = pic
    rsp = lcp_request(app_mac_key_id, app_mac_key, 'POST', url, req_body, cid=cid, print_rsp=True)
    return rsp


########################################################################################################################
def update_order_status(order_url: str, credit_status: str, cid: str):
    print("------------ UPDATING ORDER STATUS ------------")
    if credit_status == "success":
        order_status = "complete"
    elif credit_status == "pending":
        order_status = "creditPending"
    elif credit_status == "systemError":
        order_status = "creditError"
    elif credit_status == "failure":
        order_status = "creditFailed"
    req_body = {
        "status": order_status
    }
    rsp = lcp_request(app_mac_key_id, app_mac_key, 'PATCH', order_url, req_body, cid=cid, print_rsp=True)
    return rsp


########################################################################################################################
def manual_bonus(parent_order_url: str, offer_url: str, ticket: str, cid: str):
    log = {
        "parent_order": parent_order_url,
        "offer": offer_url,
        "pts_app_cid": cid,
        "ticket": ticket,
        "parent_order_amount": None,
        "bonus_amount": None,
        "order_url": None,
        "order_status": None,
        "credit_status": None
    }
    base_info = get_base_info(parent_order_url, cid)

    if base_info.get("base_points"):
        log["parent_order_amount"] = base_info["base_points"]
        bonus_info = get_bonus_info(base_info, offer_url, cid)

        if bonus_info.get("amount"):
            log["bonus_amount"] = bonus_info["amount"]
            mv = create_mv(base_info, cid)

            if mv.get("status"):
                mv_url = mv["links"]["self"]["href"]
                order = create_order(base_info, mv, bonus_info, parent_order_url, offer_url, ticket, cid)

                if order.get("status"):
                    log["order_url"] = order["links"]["self"]["href"]
                    link_order_to_mv(mv_url, log["order_url"], cid)
                    credit = create_credit(mv_url, bonus_info["amount"], cid, bonus_info["pic"])

                    if credit.get("status"):
                        log["credit_status"] = credit.get("status")
                        update_order_status(log["order_url"], log["credit_status"], cid)

                    get_order = lcp_request(user_mac_key_id, user_mac_key, 'GET', log["order_url"], cid=cid)
                    if get_order.get("status"):
                        log["order_status"] = get_order.get("status")
    return log


