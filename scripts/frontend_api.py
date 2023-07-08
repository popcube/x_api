import requests
import json
import sys
import random
import string

followers_url = "https://twitter.com/i/api/graphql/8slyDObmnUzBOCu7kYZj_A/UserByRestId"
queries_init = {
    "variables": {
        "userId": "",
        "withSafetyModeUserFields": True},
    "features": {
        "hidden_profile_likes_enabled": False,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "highlights_tweets_tab_ui_enabled": True,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "responsive_web_graphql_timeline_navigation_enabled": True}
}
bearer_token = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"


def get_token_from_texts(token_name, r_text):
    token_index = r_text.find(token_name + "=")
    return r_text[token_index+len(token_name)+1: r_text[token_index:].find(";") + token_index]


def frontend_api(acc_name, acc_id):

    r = requests.get("https://twitter.com/" + acc_name)
    r_text = r.text

    # csrt_token = "c26653260b4584998fd9f78bc6909dd4"

    csrt_token = ''.join(random.choices(string.hexdigits[:16], k=32))

    cookie_dic = {
        "gt": get_token_from_texts("gt", r_text),
        # "guest_id_marketing": get_token_from_texts("guest_id_marketing", r_text),
        # "guest_id_ads": get_token_from_texts("guest_id_ads", r_text),
        # "personalization_id": get_token_from_texts("personalization_id", r_text),
        "ct0": csrt_token
    }

    header_dic = {
        "X-Csrf-Token": csrt_token,
        "X-Guest-Token": cookie_dic["gt"],
        "Authorization": "Bearer " + bearer_token
    }

    queries = queries_init.copy()
    queries["variables"]["userId"] = acc_id
    for key in queries.keys():
        query_text = json.dumps(queries[key], separators=(',', ':'))
        queries[key] = query_text

    print(followers_url)
    print(cookie_dic)
    print(queries)
    print(header_dic)

    r = requests.get(followers_url, cookies=cookie_dic,
                     params=queries, headers=header_dic)
    print(r.text)
    print()
    print(r.headers)
    print(r.status_code)
    print(r.content)
    r_dic = json.loads(r.text)
    r_dic_data = r_dic["data"]["user"]["result"]["legacy"]
    # print(json.dumps(r_dic, indent=4))
    # print(r_dic_data["normal_followers_count"])
    return r_dic_data["followers_count"]


for acc_name, acc_id in (("pj_sekai", "1158668053183266816"), ("bang_dream_gbp", "775280864674525184"), ("Genshin_7", "1070960596357509121")):
    print(frontend_api(acc_name, acc_id))
