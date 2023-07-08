import requests
import json
import sys
import random
import string

followers_url = "https://twitter.com/i/api/graphql/2ICDjqPd81tulZcYrtpTuQ/TweetResultByRestId"
queries_init = {
    "variables": {
        "tweetId": "",
        "withCommunity": False,
        "includePromotedContent": False,
        "withVoice": False
    },
    "features": {
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "tweetypie_unmention_optimization_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": False,
        "tweet_awards_web_tipping_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "responsive_web_media_download_video_enabled": False,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_enhance_cards_enabled": False
    },
    "fieldToggles": {
        "withArticleRichContentState": False
    }
}
bearer_token = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

gt = ""


def get_token_from_texts(token_name, r_text):
    token_index = r_text.find(token_name + "=")
    return r_text[token_index+len(token_name)+1: r_text[token_index:].find(";") + token_index]


def frontend_api(acc_name, tw_id):
    global gt

    if len(gt) == 0:
        r = requests.get("https://twitter.com/" +
                         acc_name + "/status/" + tw_id)
        r_text = r.text
        gt = get_token_from_texts("gt", r_text)
    # print(r.text)
    # sys.exit(0)

    # csrt_token = "c26653260b4584998fd9f78bc6909dd4"

    csrt_token = ''.join(random.choices(string.hexdigits[:16], k=32))

    cookie_dic = {
        "gt": gt,
        # "guest_id_marketing": get_token_from_texts("guest_id_marketing", r_text),
        # "guest_id_ads": get_token_from_texts("guest_id_ads", r_text),
        # "personalization_id": get_token_from_texts("personalization_id", r_text),
        "ct0": csrt_token
    }

    header_dic = {
        "X-Csrf-Token": csrt_token,
        "X-Guest-Token": gt,
        "Authorization": "Bearer " + bearer_token
    }

    queries = queries_init.copy()
    queries["variables"]["tweetId"] = tw_id
    for key in queries.keys():
        query_text = json.dumps(queries[key], separators=(',', ':'))
        queries[key] = query_text

    # print(followers_url)
    # print(cookie_dic)
    # print(queries)
    # print(header_dic)

    r = requests.get(followers_url, cookies=cookie_dic,
                     params=queries, headers=header_dic)
    # print(r.text)
    # print()
    # print(r.headers)
    # print(r.status_code)
    # print(r.content)
    r_dic = json.loads(r.text)
    r_dic_data = r_dic["data"]["tweetResult"]["result"]["core"]["user_results"]["result"]["legacy"]
    # print(json.dumps(r_dic, indent=4))
    # print(r_dic_data["normal_followers_count"])
    return r_dic_data["followers_count"]


acc_idx = random.sample(range(3), 3)
acc_data = (("pj_sekai", "1676474549871996928"), ("bang_dream_gbp",
            "1674659638174789632"), ("Genshin_7", "1675716141874855937"))
for idx in acc_idx:
    acc_name, tw_id = acc_data[idx]
    print("acc: " + acc_name)
    print(frontend_api(acc_name, tw_id))
