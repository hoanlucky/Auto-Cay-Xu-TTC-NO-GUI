import re
import uuid
import time
import json
import httpx
import base64
import random
from datetime import datetime

reaction_map = {
    "like": "1635855486666999",
    "love": "1678524932434102",
    "haha": "115940658764963",
    "wow": "478547315650144",
    "sad": "613557422527858",
    "angry": "444813342392137",
    "care": "613557422527858"
}

function_id = {
    "reaction": "9232085126871383",
    "comment": "9601922916568790",
    "follow": "9958189347559799",
    "like_page": "6716077648448761",
    "share": "29186751774272984",
    "join_group": "9208589639268737",
    "review_page": "29186751774272984"
}

activate = ""
command = ""

cookie_TTC = ""
cookie_FB = ""
fb_dtsg_fb = ""
# function_id = "9232085126871383"
delay_a_job = 0
delay_loop = 0
amount_job_run = 0
on_job = None
total_coin = 0


def introduction():
    print("\033[1;95m╔═════════════════════════════════════════╗\033[0m")
    print("\033[1;95m║\033[0m     🚀 \033[96mTOOL TỰ ĐỘNG CÀY XU TTC\033[0m 🚀       \033[1;95m║\033[0m")
    print("\033[1;95m╠═════════════════════════════════════════╣\033[0m")
    print("\033[1;95m║\033[0m👤 \033[93mBản quyền    \033[0m: Lê Công Hoan           \033[1;95m║\033[0m")
    print("\033[1;95m║\033[0m📞 \033[93mSố điện thoại\033[0m: 036 9723 106           \033[1;95m║\033[0m")
    print("\033[1;95m║\033[0m📺 \033[93mYouTube      \033[0m: youtube.com/@hoanlucky \033[1;95m║\033[0m")
    print("\033[1;95m║\033[0m🌐 \033[93mWebsite      \033[0m: handtrickes.com        \033[1;95m║\033[0m")
    print("\033[1;95m╚═════════════════════════════════════════╝\033[0m\n")

def set_config():
    global reaction_map, function_id, activate, command
    response = httpx.get("https://handtrickes.com/Tools/AutoTTC_NoGuiV1.txt", timeout=30)
    response.raise_for_status()
    data = response.json()
    activate = data.get("activate")
    reaction_map = data.get("reaction_map", {})
    function_id = data.get("function_id", {})
    command = data.get("command")
    if "no" in activate.lower():
        introduction()
        print("\033[1;95m╔═════════════════════════════════════════╗\033[0m")
        print("\033[1;95m║\033[0m        👷‍♂️ \033[1;93mHỆ THỐNG ĐANG BẢO TRÌ\033[0m\033[1;95m         ║\033[0m")
        print("\033[1;95m╚═════════════════════════════════════════╝\033[0m\n")
        exit()
    while True:
        print("Lấy mã kích hoạt tại: https://handtrickes.com/tools/ttc")
        key_activate = input("Nhập mã kích hoạt: ")
        response = httpx.post("https://handtrickes.com/api/tools/ttc", data={"keyttc": key_activate}, timeout=30)
        data = response.json()
        code = data.get('code')
        if "0" == code:
            print(f"❌ Mã kích hoạt không chính xác.")
        elif "2" == code:
            print(f"❌ Mã kích hoạt đã hết hạn.")
        else:
            break
    introduction()

set_config()


def set_fb_dtsg(cookie_: str):
    global fb_dtsg_fb
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding: identity",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-platform-version": '"19.0.0"',
        "sec-ch-ua-full-version-list": '"Google Chrome";v="135.0.7049.97", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.97"',
        "viewport-width": "1368",
    }

    cookies = {
        k.strip(): v for k, v in [
            item.split("=", 1) for item in cookie_.strip().split(";") if "=" in item
        ]
    }

    with httpx.Client(headers=headers) as client:
        response = client.get("https://www.facebook.com", cookies=cookies, follow_redirects=True, timeout=30)
        try:
            fb_dtsg_fb = response.text.split('"fb_dtsg","value":"')[1].split('"},{')[0]
        except:
            print("❌ Cookie Facebook không hợp lệ!")
            exit()
        return fb_dtsg_fb

def add_total_coin(text):
    global total_coin
    text = text.split("cộng")[1]
    match = re.search(r'\d+', text)
    coin = int(match.group()) if match else 0
    total_coin = total_coin + coin

def send_reaction(feedback_id: str, reaction: str):
    global cookie_FB, fb_dtsg_fb, function_id, reaction_map
    cookie_ = cookie_FB
    actor_id = cookie_FB.split("c_user=")[1].split(";")[0]
    reaction_id = reaction_map.get(reaction.lower())
    doc_id_fb = function_id.get("reaction")
    if not reaction_id:
        print(f"❌ Phản ứng không hợp lệ: {reaction}")
        return

    headers = {
        "authority": "www.facebook.com",
        "method": "POST",
        "path": "/api/graphql/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"{cookie_}",  # cookie của bạn
        "origin": "https://www.facebook.com",
        "priority": "u=1, i",
        "referer": "https://www.facebook.com",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-fb-friendly-name": "UfiReactionMutation",
        "x-fb-lsd": "-NbvTKeQzrBH7Fp5RKqdVj"
    }

    payload = {
        "fb_dtsg": f"{fb_dtsg_fb}",  # Lấy fb_dtsg từ cookies hoặc HTML
        "variables": '{"input":{"attribution_id_v2":"CometSinglePostDialogRoot.react,comet.post.single_dialog,via_cold_start,1744983330653,395874,,,","feedback_id":"'+f'{feedback_id}'+'","feedback_reaction_id":"'+f'{reaction_id}'+'","feedback_source":"OBJECT","is_tracking_encrypted":true,"tracking":["AZXDDdKvynSo_-0XlyWPvGcQI24lxY9uif_eMRwA_MP7RaVOGT1AwHrwfz5Joegz_0e6aa-j7AulaPbygpP84rSbKHWas6rpvi7C23MpYtI_2oiajjL4vPaec-_RSodF51STzcdyitLWWX5vp75yDxXDhMY2OgVDtjpAK5mu8hTisN0Jp9CRbK7xWzPmSutctiAOgrzFJe7RzlwK1zPw6Hf_8aqWb11WVJbD92d0-vnUKvof74BsuG2IKOEXHddAIrb_jK6bk1DpghCfS5KGMF9BbeLrFZDdm0FM6DIZNjlVFIupDHbdmfzevzB3c_uNL131GPukaoqtmWWpvCeQBli9Fc7dS7RZ-54WRqhJG8ZZOUcdT0SBcTUtFV_MrSxA7KlueOXWL_T9O26shCU5GEvf8-7rTCA6k5RXk-lm226mGMMTG9tS7XNrxuOv38DbMbHNde8k7lUNvjSjcWG8-kCRq4TNzeWLaMmzqYEyuwuInoXRuTwLAYX24vLW6apqUYLxuu_B8jN70jQ-534dLPV26J_oDtY6qLQHzrJoTw0aeNGuFjqld0peBUjvUX5RFF3esuoNxQd4oAiNQrmgkA8YaZ8xa3WiMeyamZTs9PziHdKg2n9p01rSTwCCkNeVLbf0X0BHLW9d0tWAABq0aN5Jnkv1DE3ln-gLbRiOSGBJ42N-FishNOVwgVrJl-akgEG7ZyJoW9uulAklzbXeqCNaIj9hcSOjDt0fqVTfb3B0ekmhqlmZcYRdpAmu7YeHnFXTEgwyDZr_AD0XwoojvIM82GTwt8lE80MtwJlR_KOr-rkTWRikz4AqBN50qoYgHnIkPqa58TUmFQk_48ZduDLp5HtxncDN4HIH6pdn1OiPKruxzhrRefTjDQusSBBYi4KrBxmBcF_Kl_9emBg4rkhjlYwffNu-vBqSouZRy1aiQjuM95Y_p-N8CN8RXjnY6Hrq_b_Hxszd2A7v0U-Wn-2g5h-SmTrPw7XWaYCwjzItU9JSwts_4BsyLtLRD7yjRn6vI6pHbdVzjakDg2nAvabrd1BWl4eIY77HDHHsANkNVPesPxARGXICLyu8j0IA1yvjfPb45C_5zOmsj-VFYIE9HF3h1ndkGcYi9YDW370oz0jWLtAbJKdy_E9hsXK9mdYSCRjF-9FqkA7C_Omqd5zQP83jgnp4NpB_DZi9S4vdxbjtopJrki7ugAMlP5niEQusWU1oplZfjqOwcJ_TS7ZuHL4GoLhHBxNVDHKDnP5Xzwr62Jlxq7_lHLVEpEgfjfHcjd6LPNp0d-DmNyl_OEr7Vb23xX_x66TjH-x5WVQesv6nYBVmNNGkrV_9EdaWdDqaoBuM4r-HnfY04eUTnl501MsvOKjj6Qz6rOJdqfeUPQ"],"session_id":"8cb5e720-0d14-4756-abe8-ce9868b1d9e5","actor_id":"'+f'{actor_id}'+'","client_mutation_id":"1"},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}',
        "server_timestamps": "true",
        "doc_id": f"{doc_id_fb}"  # ID của tài liệu hành động, thường lấy từ HTML hoặc API
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post("https://www.facebook.com/api/graphql/", headers=headers, data=payload)
            if response.status_code == 200:
                # print("✅ Đã gửi phản ứng thành công!")
                pass
            else:
                print(f"❌ Gửi thất bại: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Lỗi xảy ra khi gửi phản ứng: {e}")


def send_comment(feedback_id: str, text_content: str, id_post):
    global cookie_FB, fb_dtsg_fb, function_id, reaction_map
    cookie_ = cookie_FB
    actor_id = cookie_FB.split("c_user=")[1].split(";")[0]
    doc_id_fb = function_id.get("comment")

    headers = {
        "authority": "www.facebook.com",
        "method": "POST",
        "path": "/api/graphql/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"sb=dNklY5v3ZseMQ892HzesCZy5; ps_n=1; ps_l=1; datr=QVCzZws2VW28qIiTchRLUnho; locale=vi_VN; vpd=v1%3B858x400x2; wl_cbv=v2%3Bclient_version%3A2791%3Btimestamp%3A1745147738; dpr=1; c_user=100085459523549; xs=14%3AvGD1lWQxglWxSw%3A2%3A1745149379%3A-1%3A14114; fr=11Dz6HWlNHVljPVKd.AWflkPDVsckSoKSx21VM4SyUD1rH6XBkbaHoenLH6_mFF4KYAwk.BoBNZn..AAA.0.0.BoBN3J.AWdsWLXblO7ti9vMK8jh_rclooA; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1745149391360%2C%22v%22%3A1%7D; wd=1368x945",
        "origin": "https://www.facebook.com",
        "priority": "u=1, i",
        "referer": f"https://www.facebook.com/{id_post}",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-fb-friendly-name": "useCometUFICreateCommentMutation",
        "x-fb-lsd": "-NbvTKeQzrBH7Fp5RKqdVj"
    }
    
    payload = {
        "fb_dtsg": f"{fb_dtsg_fb}",
        "variables": '{"feedLocation":"PERMALINK","feedbackSource":2,"groupID":null,"input":{"client_mutation_id":"31","actor_id":"'+str(actor_id)+'","attachments":null,"feedback_id":"'+str(feedback_id)+'","formatting_style":null,"message":{"ranges":[],"text":"'+str(text_content)+'"},"attribution_id_v2":"CometSinglePostDialogRoot.react,comet.post.single_dialog,unexpected,1745150415870,470174,,,;CometHomeRoot.react,comet.home,via_cold_start,1745149506051,943147,4748854339,229#230#301#301,","vod_video_timestamp":null,"is_tracking_encrypted":true,"tracking":["{\\"assistant_caller\\":\\"comet_above_composer\\",\\"conversation_guide_session_id\\":\\"01bac1c2-a633-4d7e-be1f-956985778d1c\\",\\"conversation_guide_shown\\":null}"],"feedback_source":"OBJECT","idempotence_token":"'+f'client:{uuid.uuid4()}'+'","session_id":"f37db23e-e946-4e93-9ba8-c128bd1abf70"},"inviteShortLinkKey":null,"renderLocation":null,"scale":1,"useDefaultActor":false,"focusCommentID":null,"__relay_internal__pv__IsWorkUserrelayprovider":false}',
        "server_timestamps": "true",
        "doc_id": f"{doc_id_fb}"
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post("https://www.facebook.com/api/graphql/", headers=headers, data=payload)
            if response.status_code == 200:
                # print("✅ Đã gửi phản ứng thành công!")
                pass
            else:
                print(f"❌ Gửi thất bại: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Lỗi xảy ra khi gửi phản ứng: {e}")


def send_follow(id_profile: str):
    global cookie_FB, fb_dtsg_fb, function_id
    cookie_ = cookie_FB
    actor_id = cookie_FB.split("c_user=")[1].split(";")[0]
    doc_id_fb = function_id.get("follow")

    headers = {
        "authority": "www.facebook.com",
        "method": "POST",
        "path": "/api/graphql/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"{cookie_}",  # cookie của bạn
        "origin": "https://www.facebook.com",
        "priority": "u=1, i",
        "referer": "https://www.facebook.com",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-fb-friendly-name": "CometUserFollowMutation",
        "x-fb-lsd": "EWrSm8xvyCgoebc3J3iGec"
    }

    payload = {
        "fb_dtsg": f"{fb_dtsg_fb}",  # Lấy fb_dtsg từ cookies hoặc HTML
        "variables": '{"input":{"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,unexpected,1745159401291,513849,250100865708545,,;CometSinglePostDialogRoot.react,comet.post.single_dialog,unexpected,1745150415870,470174,,304#10#230#301,;CometHomeRoot.react,comet.home,via_cold_start,1745149506051,943147,4748854339,229#230#301#301,","is_tracking_encrypted":false,"subscribe_location":"PROFILE","subscribee_id":"'+str(id_profile)+'","tracking":null,"actor_id":"'+str(actor_id)+'","client_mutation_id":"21"},"scale":1}',
        "server_timestamps": "true",
        "doc_id": f"{doc_id_fb}"  # ID của tài liệu hành động, thường lấy từ HTML hoặc API
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post("https://www.facebook.com/api/graphql/", headers=headers, data=payload)
            if response.status_code == 200:
                # print("✅ Đã gửi phản ứng thành công!")
                pass
            else:
                print(f"❌ Gửi thất bại: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Lỗi xảy ra khi gửi phản ứng: {e}")


def send_like_page(id_page: str):
    global cookie_FB, fb_dtsg_fb, function_id
    cookie_ = cookie_FB
    actor_id = cookie_FB.split("c_user=")[1].split(";")[0]
    doc_id_fb = function_id.get("like_page")

    headers = {
        "authority": "www.facebook.com",
        "method": "POST",
        "path": "/api/graphql/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"{cookie_}",  # cookie của bạn
        "origin": "https://www.facebook.com",
        "priority": "u=1, i",
        "referer": "https://www.facebook.com",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-fb-friendly-name": "CometProfilePlusLikeMutation",
        "x-fb-lsd": "EWrSm8xvyCgoebc3J3iGec"
    }

    payload = {
        "fb_dtsg": f"{fb_dtsg_fb}",  # Lấy fb_dtsg từ cookies hoặc HTML
        "variables": '{"input":{"is_tracking_encrypted":false,"page_id":"'+str(id_page)+'","source":null,"tracking":null,"actor_id":"'+str(actor_id)+'","client_mutation_id":"22"},"scale":1}',
        "server_timestamps": "true",
        "doc_id": f"{doc_id_fb}"  # ID của tài liệu hành động, thường lấy từ HTML hoặc API
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post("https://www.facebook.com/api/graphql/", headers=headers, data=payload)
            if response.status_code == 200:
                # print("✅ Đã gửi phản ứng thành công!")
                pass
            else:
                print(f"❌ Gửi thất bại: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Lỗi xảy ra khi gửi phản ứng: {e}")



def send_share(id_post: str, text_content: str):
    global cookie_FB, fb_dtsg_fb, function_id
    cookie_ = cookie_FB
    actor_id = cookie_FB.split("c_user=")[1].split(";")[0]
    doc_id_fb = function_id.get("share")

    headers = {
        "authority": "www.facebook.com",
        "method": "POST",
        "path": "/api/graphql/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"{cookie_}",  # cookie của bạn
        "origin": "https://www.facebook.com",
        "priority": "u=1, i",
        "referer": "https://www.facebook.com",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-fb-friendly-name": "ComposerStoryCreateMutation",
        "x-fb-lsd": "EWrSm8xvyCgoebc3J3iGec"
    }

    payload = {
        "fb_dtsg": f"{fb_dtsg_fb}",  # Lấy fb_dtsg từ cookies hoặc HTML
        "variables": '{"input":{"composer_entry_point":"share_modal","composer_source_surface":"feed_story","composer_type":"share","idempotence_token":"'+f'{uuid.uuid4()}'+'_FEED","source":"WWW","attachments":[{"link":{"share_scrape_data":"{\\"share_type\\":22,\\"share_params\\":['+str(id_post)+']}"'+'}'+'}'+'],"reshare_original_post":"RESHARE_ORIGINAL_POST","audience":{"privacy":{"allow":[],"base_state":"EVERYONE","deny":[],"tag_expansion_state":"UNSPECIFIED"'+'}'+'}'+',"is_tracking_encrypted":true,"tracking":["AZXb7WVf_w9oryRUMCBOBlwsR1rdtj8JULgM4oDWFiawDIqxFC39JPeQGDf7_lULsparE-4Nw-B_o23QkVWyXxl7SrUUTIznXHFb6PM4AVLFrzB2I7sYxI0MrymZLaVzn4WP5Ru3Ns2GMcKE6Zut7Q4KoAfNLBVA8HTjc5TlHdwKD1WBtRQ2782GVDRE3JFVfrhAUuHEdDiy2tP1r529Qwsmeeya1PHFzTFMg5ykoL2eJgZgxe1GQmN9U7fEHqHCPkBlPWY1dTQUbgAYcmGGJbJaYAMCiB2cv2-tlrXn-y_wJaPqFd-nMdYOCIUsX0GjSffXvAXW_IYfZxUboug68NnqOp9xq4OpD4i0aj-ZVyDPheDpya7uOIWqMfkwdo_muW2e0oe85-5ecVVS-OV3QzZ5lu6AsyTDjtC-_D9G-PholyDpE33h-qTokj6l8yex3bJ7RpR3vav-3SQlFHb3gxH6HL6dMLpy6qgl5gISnStc3RmgNjB0oHSjnEzZgNdXiTnB5AuWuMKSO6sQtRz4xW9t-qw01hLwVigFvYqJjxnpyft4glpr4lQwiKZmAglSxm0HmOSZ6ZZ0H4u9VMh9eCMhMTN7fDfiqe1VlwetFhcGrqCW4oxKzDqxZ88Tnz_vOrDESObNy8rYsQIZEAOLcWHqtAwS61GdXb-PaGl9wSNWnjQ8MFQdxmn_CFkydyajN72zx6YRIOUx4NjEKV5IpTm3Q3tkKXcVJD1ITV4IrHWo7RSIWDy947B-i6ijshzzQ5zBsMc1hggdyQXxCeUxr6oh6RoLjjWv6b9A9Mtg1hD39ncDY3xOrkr7EIfKA3ZwVlGhnb8GB96tHfWY8jOG6f2XUKZLw4RuqEYuEBFO4oKyx3h0GiGKhp6TM2sQ-1nE5cg",null],"message":{"ranges":[],"text":"'+str(text_content)+'"},"logging":{"composer_session_id":"4a6c6d30-3ecb-4e1a-9b8e-23875b63fe91"},"navigation_data":{"attribution_id_v2":"CometHomeRoot.react,comet.home,tap_tabbar,1745160888049,516992,4748854339,,"},"event_share_metadata":{"surface":"newsfeed"},"actor_id":"'+str(actor_id)+'","client_mutation_id":"24"},"feedLocation":"NEWSFEED","feedbackSource":1,"focusCommentID":null,"gridMediaWidth":null,"groupID":null,"scale":1,"privacySelectorRenderLocation":"COMET_STREAM","checkPhotosToReelsUpsellEligibility":false,"renderLocation":"homepage_stream","useDefaultActor":false,"inviteShortLinkKey":null,"isFeed":true,"isFundraiser":false,"isFunFactPost":false,"isGroup":false,"isEvent":false,"isTimeline":false,"isSocialLearning":false,"isPageNewsFeed":false,"isProfileReviews":false,"isWorkSharedDraft":false,"hashtag":null,"canUserManageOffers":false,"__relay_internal__pv__CometUFIShareActionMigrationrelayprovider":true,"__relay_internal__pv__GHLShouldChangeSponsoredDataFieldNamerelayprovider":false,"__relay_internal__pv__GHLShouldChangeAdIdFieldNamerelayprovider":true,"__relay_internal__pv__CometIsReplyPagerDisabledrelayprovider":false,"__relay_internal__pv__IsWorkUserrelayprovider":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false,"__relay_internal__pv__FBReels_deprecate_short_form_video_context_gkrelayprovider":true,"__relay_internal__pv__CometFeedStoryDynamicResolutionPhotoAttachmentRenderer_experimentWidthrelayprovider":500,"__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider":false,"__relay_internal__pv__WorkCometIsEmployeeGKProviderrelayprovider":false,"__relay_internal__pv__IsMergQAPollsrelayprovider":false,"__relay_internal__pv__FBReelsMediaFooter_comet_enable_reels_ads_gkrelayprovider":false,"__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider":true,"__relay_internal__pv__CometFeedPYMKHScrollInitialPaginationCountrelayprovider":10,"__relay_internal__pv__FBReelsIFUTileContent_reelsIFUPlayOnHoverrelayprovider":false,"__relay_internal__pv__GHLShouldChangeSponsoredAuctionDistanceFieldNamerelayprovider":true}',
        "server_timestamps": "true",
        "doc_id": f"{doc_id_fb}"  # ID của tài liệu hành động, thường lấy từ HTML hoặc API
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post("https://www.facebook.com/api/graphql/", headers=headers, data=payload)
            if response.status_code == 200:
                # print("✅ Đã gửi phản ứng thành công!")
                pass
            else:
                print(f"❌ Gửi thất bại: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Lỗi xảy ra khi gửi phản ứng: {e}")



def send_join_group(id_group: str):
    global cookie_FB, fb_dtsg_fb, function_id
    cookie_ = cookie_FB
    actor_id = cookie_FB.split("c_user=")[1].split(";")[0]
    doc_id_fb = function_id.get("join_group")

    headers = {
        "authority": "www.facebook.com",
        "method": "POST",
        "path": "/api/graphql/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"{cookie_}",  # cookie của bạn
        "origin": "https://www.facebook.com",
        "priority": "u=1, i",
        "referer": "https://www.facebook.com",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-fb-friendly-name": "CometProfilePlusLikeMutation",
        "x-fb-lsd": "EWrSm8xvyCgoebc3J3iGec"
    }

    payload = {
        "fb_dtsg": f"{fb_dtsg_fb}",  # Lấy fb_dtsg từ cookies hoặc HTML
        "variables": '{"feedType":"DISCUSSION","groupID":"'+str(id_group)+'","input":{"action_source":"GROUP_MALL","attribution_id_v2":"CometGroupDiscussionRoot.react,comet.group,unexpected,1745162984398,86551,2361831622,,;GroupsCometSearchRoot.react,comet.groups.search,tap_scoped_search_bar,1745162978392,45031,,,;GroupsCometCrossGroupFeedRoot.react,comet.groups.feed,tap_bookmark,1745162967643,918963,2361831622,,","group_id":"'+str(id_group)+'"},"actor_id":"'+str(actor_id)+'","client_mutation_id":"5"},"inviteShortLinkKey":null,"isChainingRecommendationUnit":false,"scale":1,"source":"GROUP_MALL","renderLocation":"group_mall","__relay_internal__pv__GroupsCometGroupChatLazyLoadLastMessageSnippetrelayprovider":false}',
        "server_timestamps": "true",
        "doc_id": f"{doc_id_fb}"  # ID của tài liệu hành động, thường lấy từ HTML hoặc API
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post("https://www.facebook.com/api/graphql/", headers=headers, data=payload)
            if response.status_code == 200:
                # print("✅ Đã gửi phản ứng thành công!")
                pass
            else:
                print(f"❌ Gửi thất bại: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Lỗi xảy ra khi gửi phản ứng: {e}")


def send_review_page(id_page: str, text_content: str):
    global cookie_FB, fb_dtsg_fb, function_id
    cookie_ = cookie_FB
    actor_id = cookie_FB.split("c_user=")[1].split(";")[0]
    doc_id_fb = function_id.get("review_page")

    headers = {
        "authority": "www.facebook.com",
        "method": "POST",
        "path": "/api/graphql/",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"{cookie_}",  # cookie của bạn
        "origin": "https://www.facebook.com",
        "priority": "u=1, i",
        "referer": "https://www.facebook.com",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-asbd-id": "359341",
        "x-fb-friendly-name": "CometProfilePlusLikeMutation",
        "x-fb-lsd": "EWrSm8xvyCgoebc3J3iGec"
    }

    payload = {
        "fb_dtsg": f"{fb_dtsg_fb}",  # Lấy fb_dtsg từ cookies hoặc HTML
        "variables": '{"input":{"composer_entry_point":"inline_composer","composer_source_surface":"page_recommendation_tab","idempotence_token":"'+f'{uuid.uuid4()}'+'_FEED","source":"WWW","audience":{"privacy":{"allow":[],"base_state":"EVERYONE","deny":[],"tag_expansion_state":"UNSPECIFIED"'+'}'+'}'+',"message":{"ranges":[],"text":"'+str(text_content)+'"},"with_tags_ids":null,"text_format_preset_id":"0","page_recommendation":{"page_id":"'+str(id_page)+'","rec_type":"POSITIVE"},"logging":{"composer_session_id":"0994e4a9-d857-484c-91f7-c8936eca5589"},"navigation_data":{"attribution_id_v2":"ProfileCometReviewsTabRoot.react,comet.profile.reviews,via_cold_start,1745163947335,492122,250100865708545,,"},"tracking":[null],"event_share_metadata":{"surface":"newsfeed"},"actor_id":"'+str(actor_id)+'","client_mutation_id":"1"},"feedLocation":"PAGE_SURFACE_RECOMMENDATIONS","feedbackSource":0,"focusCommentID":null,"gridMediaWidth":null,"groupID":null,"scale":1,"privacySelectorRenderLocation":"COMET_STREAM","checkPhotosToReelsUpsellEligibility":false,"renderLocation":"timeline","useDefaultActor":false,"inviteShortLinkKey":null,"isFeed":false,"isFundraiser":false,"isFunFactPost":false,"isGroup":false,"isEvent":false,"isTimeline":true,"isSocialLearning":false,"isPageNewsFeed":false,"isProfileReviews":true,"isWorkSharedDraft":false,"hashtag":null,"canUserManageOffers":false,"__relay_internal__pv__CometUFIShareActionMigrationrelayprovider":true,"__relay_internal__pv__GHLShouldChangeSponsoredDataFieldNamerelayprovider":false,"__relay_internal__pv__GHLShouldChangeAdIdFieldNamerelayprovider":true,"__relay_internal__pv__CometIsReplyPagerDisabledrelayprovider":false,"__relay_internal__pv__IsWorkUserrelayprovider":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false,"__relay_internal__pv__FBReels_deprecate_short_form_video_context_gkrelayprovider":true,"__relay_internal__pv__CometFeedStoryDynamicResolutionPhotoAttachmentRenderer_experimentWidthrelayprovider":500,"__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider":false,"__relay_internal__pv__WorkCometIsEmployeeGKProviderrelayprovider":false,"__relay_internal__pv__IsMergQAPollsrelayprovider":false,"__relay_internal__pv__FBReelsMediaFooter_comet_enable_reels_ads_gkrelayprovider":false,"__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider":true,"__relay_internal__pv__CometFeedPYMKHScrollInitialPaginationCountrelayprovider":10,"__relay_internal__pv__FBReelsIFUTileContent_reelsIFUPlayOnHoverrelayprovider":false,"__relay_internal__pv__GHLShouldChangeSponsoredAuctionDistanceFieldNamerelayprovider":true}',
        "server_timestamps": "true",
        "doc_id": f"{doc_id_fb}"  # ID của tài liệu hành động, thường lấy từ HTML hoặc API
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post("https://www.facebook.com/api/graphql/", headers=headers, data=payload)
            if response.status_code == 200:
                # print("✅ Đã gửi phản ứng thành công!")
                pass
            else:
                print(f"❌ Gửi thất bại: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Lỗi xảy ra khi gửi phản ứng: {e}")



def get_job(path):
    global cookie_TTC, amount_job_run
    url = f"https://tuongtaccheo.com/{path}getpost.php"
    cookie_ = cookie_TTC
    headers = {
        "authority": "tuongtaccheo.com",
        "method": "GET",
        "path": f"/{path}getpost.php",
        "scheme": "https",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"{cookie_}",
        "priority": "u=1, i",
        "referer": f"https://tuongtaccheo.com/{path}",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                # print("✅ Đã lấy job thành công!")
                jobs = json.loads(response.text)
                return jobs[:amount_job_run]
            else:
                print(f"❌ Lấy job thất bại: {response.status_code} - {response.text}")
                return []
    except Exception as e:
        print(f"⚠️ Lỗi xảy ra khi lấy job: {e}")
        return []


def get_coin(id_job, url):
    global cookie_TTC
    url = f"https://tuongtaccheo.com/{url}nhantien.php"
    cookie_ = cookie_TTC
    headers = {
        "authority": "tuongtaccheo.com",
        "method": "POST",
        "path": f"/{url}nhantien.php",
        "scheme": "https",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": f"{cookie_}",
        "origin": "https://tuongtaccheo.com",
        "priority": "u=1, i",
        "referer": f"https://tuongtaccheo.com/{url}",
        "sec-ch-prefers-color-scheme": "light",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

    data = {
        "id": f"{id_job}"
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=headers, data=data)
            if response.status_code == 200:
                result = json.loads(response.text)
                if result.get('mess'):
                    print(f"✅ \033[92m{result['mess']}\033[0m")
                    add_total_coin(result['mess'])
                else:
                    print(f"❌ \033[91m{result['error']}\033[0m")
            else:
                print("❌ "+f"\033[91mNhận xu thất bại: {response.status_code} - {response.text}\033[0m")
                return
    except Exception as e:
        print("⚠️ "+f"\033[91mNhận xu thất bại: {e}\033[0m")
        return


print("Chọn job để chạy (ví dụ: 1,3,7):")
print("1. Like chéo VIP")
print("2. Cảm xúc chéo VIP")
print("3. Bình luận chéo")
print("4. Theo dõi chéo")
print("5. Like page chéo")
print("6. Share chéo")
print("7. Share chéo có nội dung")
print("8. Đánh giá page chéo")
print("9. Tham gia nhóm chéo (bảo trì)")

while True:
    on_job = input("\nNhập vào job muốn chạy: ")
    if on_job:
        on_job = on_job.replace(" ", "").split(",")
        break
    else:
        pass

while True:
    cookie_TTC = input("\nNhập vào cookie TTC: ")
    cookie_FB = input("\nNhập vào cookie Facebook: ")
    # fb_dtsg_fb = input("\nNhập vào fb_dtsg của Facebook: ")
    # function_id = input("\nNhập vào doc_id của Facebook: ")
    amount_job_run = int(input("\nNhập vào số lượng job mỗi vòng: "))
    delay_a_job = int(input("Nhập vào delay mỗi job: "))
    delay_loop = int(input("Nhập vào delay mỗi vòng:"))
    if not cookie_TTC or not cookie_FB or not function_id or int(delay_a_job)<0 or int(delay_loop)<0 or int(amount_job_run)<0:
        pass
    else:
        print("Đang kiểm tra thông tin...\n")
        set_fb_dtsg(cookie_FB)
        break


while True:
    if "1" in on_job:
        path = "kiemtien/likepostvipcheo/"
        jobs = get_job(path)
        for job in jobs:
            id_job = job['idpost']
            idfb = f"feedback:{job['idfb']}"
            feedback_id = str(base64.b64encode(idfb.encode()).decode())
            reaction = "like"
            send_reaction(feedback_id, reaction)
            get_coin(id_job, path)
            print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")
            time.sleep(delay_a_job)

    if "2" in on_job:
        path = "kiemtien/camxucvipcheo/"
        jobs = get_job(path)
        for job in jobs:
            id_job = job['idpost']
            idfb = f"feedback:{job['idfb']}"
            feedback_id = str(base64.b64encode(idfb.encode()).decode())
            reaction = job['loaicx']
            send_reaction(feedback_id, reaction)
            get_coin(id_job, path)
            print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")
            time.sleep(delay_a_job)

    if "3" in on_job:
        path = "kiemtien/cmtcheo/"
        jobs = get_job(path)
        for job in jobs:
            id_job = job['idpost']
            idfb = f"feedback:{job['idpost']}"
            feedback_id = str(base64.b64encode(idfb.encode()).decode())
            list_cmt = json.loads(job['nd'])
            content_cmt = random.choice(list_cmt)
            send_comment(feedback_id, content_cmt, job['idpost'])
            get_coin(id_job, path)
            print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")
            time.sleep(delay_a_job)

    if "4" in on_job:
        path = "kiemtien/subcheo/"
        jobs = get_job(path)
        for job in jobs:
            id_job = job['idpost']
            send_follow(str(id_job))
            get_coin(id_job, path)
            print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")
            time.sleep(delay_a_job)


    if "5" in on_job:
        path = "kiemtien/likepagecheo/"
        jobs = get_job(path)
        for job in jobs:
            id_job = job['idpost']
            send_like_page(str(id_job))
            get_coin(id_job, path)
            print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")
            time.sleep(delay_a_job)

    if "6" in on_job:
        path = "kiemtien/sharecheo/"
        jobs = get_job(path)
        for job in jobs:
            id_job = job['idpost']
            send_share(str(id_job), "")
            get_coin(id_job, path)
            print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")
            time.sleep(delay_a_job)

    if "7" in on_job:
        path = "kiemtien/sharecheokemnoidung/"
        jobs = get_job(path)
        for job in jobs:
            id_job = job['idpost']
            list_nd = json.loads(job['nd'])
            content_nd = random.choice(list_nd)
            send_share(str(id_job), content_nd)
            get_coin(id_job, path)
            print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")
            time.sleep(delay_a_job)

    if "8" in on_job:
        path = "kiemtien/danhgiapage/"
        jobs = get_job(path)
        for job in jobs:
            id_job = job['UID']
            list_nd = json.loads(job['nd'])
            content_nd = random.choice(list_nd)
            send_review_page(str(id_job), content_nd)
            get_coin(id_job, path)
            print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")
            time.sleep(delay_a_job)

    if "9" in on_job:
        print("\033[91mNhiệm vụ tham gia nhóm đang bảo trì\033[0m")
        print(f"Coin đã đào: {total_coin} - Đợi delay {delay_a_job} giây...")


    # if 1== random.randint(1,3):
    #     introduction()

    print(f"\nXong 1 vòng - Đợi delay {delay_loop} giây...")
    exec(command)
    time.sleep(delay_loop)
