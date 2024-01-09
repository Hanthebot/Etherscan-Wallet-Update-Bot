import time
import telepot
from telepot.loop import MessageLoop

from util import randString, load_userData, load_manifest, save_userData, user_default, set_user_default, link_to_tx, check_data_validity
from util_crawl import get_tx

light_data = {
    "invitation_code": randString(),
    "alive": True
}

commands = {
        "refresh_code": "",
        "code": "",
        "add_link": "add_link [account address or url]",
        "delete_link":"delete_link [account address or url]",
        "my_links": "",
        "my_hashes": "",
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
    elif command == "add_link":
        if (not len(msg.split(" ")) > 1 and ("/".join(msg.split(" ")[1].split("/")[:-1]) not in ["https://etherscan.io/tokentxns", "https://etherscan.io/address", ""])):
            bot.sendMessage(chat_id, "Invalid link")
            return
        wallet_addr = link_to_tx(msg.split(" ")[1])
        if wallet_addr in userData["userData"][str(chat_id)]["links"]:
            bot.sendMessage(chat_id, "Already in the subscription list")
            return
        userData["userData"][str(chat_id)]["links"].append(wallet_addr)
        check_data_validity(userData)
        bot.sendMessage(chat_id, "Links: \n" + "\n".join(userData["userData"][str(chat_id)]["links"]))
    elif command == "delete_link":
        if (not len(msg.split(" ")) > 1 and ("/".join(msg.split(" ")[1].split("/")[:-1]) not in ["https://etherscan.io/tokentxns", "https://etherscan.io/address", ""])):
            bot.sendMessage(chat_id, "Invalid link")
            return
        wallet_addr = link_to_tx(msg.split(" ")[1])
        if wallet_addr not in userData["userData"][str(chat_id)]["links"]:
            bot.sendMessage(chat_id, "No such address in the list")
            return
        addr_index = userData["userData"][str(chat_id)]["links"].index(wallet_addr)
        del userData["userData"][str(chat_id)]["links"][addr_index]
        check_data_validity(userData)
        bot.sendMessage(chat_id, "Links: \n" + "\n".join(userData["userData"][str(chat_id)]["links"]))
    elif command == "my_links":
        bot.sendMessage(chat_id, "Links: \n" + "\n".join(userData["userData"][str(chat_id)]["links"]))
    elif command == "my_hashes":
        bot.sendMessage(chat_id, "Links: \n" + "\n".join([f"{addr}: {userData['data'][addr][0]}, {userData['data'][addr][1]:.02f}" for addr in userData["userData"][str(chat_id)]["links"]]))
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
    check_data_validity(userData)
    prev = {addr:userData["data"][addr][:] for addr in userData["data"]}

    bot = telepot.Bot(token=manifest["bot_token"])
    MessageLoop(bot, handle).run_as_thread()
    print("Running...")
    bot.sendMessage(manifest["developer"], "Setted up")

    while light_data["alive"]:
        if time.time() % 60 < 10:
            for addr in userData["data"]:
                tempHash, tempAmt = get_tx(addr)
                if tempHash != None:
                    userData["data"][addr][0] = tempHash
                if (prev.get(addr, [None])[0] != userData["data"][addr][0]):
                    if tempAmt != None:
                        userData["data"][addr][1] = tempAmt
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] \nat {addr} \n{prev.get(addr, [None])[0]} -> {userData['data'][addr][0]} \nAmount: {prev.get(addr, [None,0.0])[1]:.02f} -> {userData['data'][addr][1]:.02f}")
            # save if there is any change
            if (prev != userData["data"]):
                save_userData(userData)
            # if there is a difference, send a message
            for user_id, user_info in userData["userData"].items():
                for addr in user_info["links"]:
                    if (userData["data"].get(addr, None) == None):
                        continue
                    if (userData["data"][addr][0] != prev.get(addr, [None])[0]):
                        # do smth here, shout out!
                        bot.sendMessage(user_info["id"], 
                            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] \nat {addr} \n{prev.get(addr, [None])[0]} -> {userData['data'][addr][0]} \nAmount: {prev.get(addr, [None,0.0])[1]:.02f} -> {userData['data'][addr][1]:.02f}")
            prev = {addr:userData["data"][addr][:] for addr in userData["data"]}
            time.sleep(10)
        else:
            time.sleep(5)