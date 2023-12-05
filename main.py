import time
import telepot
from telepot.loop import MessageLoop

from util import randString, load_userData, load_manifest, save_userData, user_default, set_user_default
from util_crawl import get_tx

light_data = {
    "invitation_code": randString(),
    "alive": True
}

commands = {
        "refresh_code": "",
        "code": "",
        "set_link": "",
        "my_link": "",
        "share_bot": "",
        "help": "",
        "terminate": "",
        "white_list": "",
        "add_white": ""
    }

def handle_msg(chat_id, command, msg):
    if command == "help":
        bot.sendMessage(chat_id, "Available commands:\n" + ", ".join(commands.keys()))
    elif command == "code":
        bot.sendMessage(chat_id, light_data["invitation_code"])
    elif command == "refresh_code":
        light_data["invitation_code"] = randString()
        bot.sendMessage(chat_id, "Done: " + light_data["invitation_code"])
    elif command == "set_link":
        if (not (len(msg.split(" ")) > 1 and msg.split(" ")[1].split("?")[0] == "https://etherscan.io/tokentxns")):
            bot.sendMessage(chat_id, "Invalid link")
            return
        userData["userData"][str(chat_id)]["link"] = msg.split(" ")[1]
        save_userData(userData)
        bot.sendMessage(chat_id, "Link -> " + msg.split(" ")[1])
    elif command == "my_link":
        bot.sendMessage(chat_id, userData["userData"][str(chat_id)]["link"])
    elif command == "share_bot":
        bot.sendMessage(chat_id, "https://t.me/" + manifest["bot_id"])
    elif command == "terminate":
        if chat_id == manifest["developer"]:
            bot.sendMessage(chat_id, "Bye")
            light_data["alive"] = False
        else:
            bot.sendMessage(chat_id, "Access denied. Please contact the developer.\n" + f"t.me/{manifest['developer_id']}")
    elif command == "add_white":
        if (not (len(msg.split(" ")) > 1 and msg.split(" ")[1].isnumeric())):
            bot.sendMessage(chat_id, "Invalid ID")
            return
        if chat_id == manifest["developer"]:
            userData["white_list"].append(int(msg.split(" ")[1]))
            save_userData(userData)
            bot.sendMessage(chat_id, "Added " + msg.split(" ")[1])
        else:
            bot.sendMessage(chat_id, "Access denied. Please contact the developer.\n" + f"t.me/{manifest['developer_id']}")
    elif command == "white_list":
        bot.sendMessage(chat_id, "Whitelist: [" + ", ".join(userData["white_list"]) + "]")

def handle(msg):
    content_type, _, chat_id = telepot.glance(msg)
    if content_type == "text":
        command = msg["text"].split(" ")[0].lower()
        if chat_id in userData["subscribers"]:
            if command in commands:
                handle_msg(chat_id, command, msg["text"])
            else:
                bot.sendMessage(chat_id, "No such command, try 'help'")
        elif command == light_data["invitation_code"] or chat_id in userData["white_list"]:
            bot.sendMessage(manifest["developer"], "Access granted to " + chat_id)
            bot.sendMessage(chat_id, "Access granted")
            userData["subscribers"].append(chat_id)
            userData["userData"][str(chat_id)] = user_default(chat_id)
            save_userData(userData)
            light_data["invitation_code"] = randString()
        else:
            bot.sendMessage(manifest["developer"], chat_id + " attempted access")
            bot.sendMessage(chat_id, "Access denied. Please contact the developer.\n" + f"t.me/{manifest['developer_id']}")

if __name__ == "__main__":
    manifest = load_manifest()
    userData = load_userData()
    set_user_default(userData)

    bot = telepot.Bot(token=manifest["bot_token"])
    MessageLoop(bot, handle).run_as_thread()
    print("Running...")
    bot.sendMessage(manifest["developer"], "Setted up")

    while light_data["alive"]:
        if time.time() % 60 < 10:
            for user_id, user_info in userData["userData"].items():
                tx_num = get_tx(user_info['link'])
                if (tx_num == None):
                    continue
                tx_hash = tx_num.get_text()
                if (tx_hash != user_info["last_hash"]):
                    # do smth here, shout out!
                    print (f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n {user_id}\n {user_info['last_hash']} -> {tx_hash}")
                    bot.sendMessage(user_info["id"], 
                        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n {user_info['last_hash']} -> {tx_hash}")
                    user_info["last_hash"] = tx_hash
                    save_userData(userData)
            time.sleep(10)
        else:
            time.sleep(5)