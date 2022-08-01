#!/use/bin/python
import re
import praw
import time
import os
import pprint

# Make sure you have praw.ini in the same folder as this with the below filled out
##[ModMail]
##client_id=
##client_secret=
##password=
##username=
##user_agent=ModMail

reddit = praw.Reddit('GOGModMail', user_agent='GOGModMail')

# This creates a text log so it can ignore mail it's already checked.
if not os.path.isfile("ModmailLog.txt"):
    ModMailLog = []
else:
    with open("ModmailLog.txt", "r") as f:
        ModMailLog = f.read()
        ModMailLog = ModMailLog.split("\n")
        ModMailLog = list(filter(None, ModMailLog))

print("Starting modmail bot...")

while True:
    try:
        #Replace with your subreddit name
        ModMailMaster = reddit.subreddit('GiftofGames').modmail
                    
        # Pulls only new modmail; remove 'state="new"' to look at all mail (may result in posts being replied to multiple times)
        ModMail = ModMailMaster.conversations(state="new")
        for mail in ModMail:
            if mail is None:
                break
            for message in mail.messages:
                # Writes modmail ID to log to skip in future checks
                if message.id not in ModMailLog:
                    ModMailLog.append(message.id)
                    with open("ModMailLog.txt", "a+") as ModMailLogOpen:
                        ModMailLogOpen.write(message.id + "\n")
                        ModMailLogOpen.close()

                    # This searches for a link to a Reddit user. This is likely a report for our subreddit, so we have the bot ignore these to allow a mod to review.
                    # If removed, may result in false positives of people reporting people breaking a specific rule instead of asking about it
                    RedditUser = re.search(r'(?i)(reddit\.com/user/|u/)', message.body_markdown)
                    if RedditUser is None:

                        # Some variables I use in multiple checks
                        Link = re.search(r'(?i)(www.|http|reddit\.com|redd.it)', message.body_markdown)
                        Steam = re.search(r'(?i)steam', message.body_markdown)
                            
                        # The general template for replying to modmail. This is copied and pasted as many times as I need a reply
                        # Search for some term in the message body. It's exactly as you type it. Regex101 is your friend.
                        Karma = re.search(r'(?i)karma', message.body_markdown)
                        # If the search is successful
                        if Karma is not None and Link is None:
                            # Reply with some canned text. \n is line break, Reddit needs 2.
                            mail.reply("There are no exceptions to the 300 comment karma rule for requesting a game or entering an offer. You may offer a game or participate in discussions without meeting this requirement. \n\nComment karma is the total number of upvotes all of your comments have. To see your karma split, hover your cursor over the total karma on your Reddit profile. \n\nRequiring 300 comment karma and a 60 day old account helps combat users attempting to circumvent the rules by making a new account. \n\nSee our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules) and [FAQ](https://www.reddit.com/r/GiftofGames/wiki/index#wiki_giftofgames_faq) for more information. \n\nThis message was sent by a bot. Please reply if it did not answer your question and a human will reply in about 48 hours.")
                            # Archives the mail so you don't need to see it.
                            mail.archive()
                            # Debug line just to print the message text to make sure you're replying to the correct messages.
##                            print(message.body_markdown)
                            # Prints in the terminal that you're replying about the keyword.
                            print("Replying to", str(mail.authors), "about karma. Archiving.")
                            # Start the loop over, starting with the next mail.
                            continue

                        Flair = re.search('(?i)flair', message.body_markdown)
                        GiftedGrabbed = re.search('(?i)(gift|grabbed|account|user|u/)', message.body_markdown)
                        if Flair is not None and GiftedGrabbed is None:
                            mail.reply("Post flair is used by simply starting the title with [REQUEST], [OFFER], etc in plain text and will be assigned by a bot. The manual selection of flair is intentionally disabled. \n\nSee our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules) and [FAQ](https://www.reddit.com/r/GiftofGames/wiki/index#wiki_giftofgames_faq) for more information. \n\nThis message was sent by a bot. Please reply if it did not answer your question and a human will reply in about 48 hours.")
                            mail.archive()
##                            print(message.body_markdown)
                            print("Replying to", mail.authors, "about flair. Archiving.")
                            continue

                        Level2 = re.search(r'(?i)level.*2', message.body_markdown)
                        PrivateProfile = re.search(r'(?i)(private|public)', message.body_markdown)
                        if Steam is not None:
                            if Level2 is not None or PrivateProfile is not None:
                                mail.reply("There are no exceptions for having a level 2 Steam profile with its library and playtime set to public for receiving Steam games. You may still offer Steam games or receive games for other platforms. \n\nThis requirement helps prevent users who have been previously banned from simply creating a new account to circumvent the rules. \n\nSee our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules) and [FAQ](https://www.reddit.com/r/GiftofGames/wiki/index#wiki_giftofgames_faq) for more information. \n\nThis message was sent by a bot. Please reply if it did not answer your question and a human will reply in about 48 hours.")
                                mail.archive()
##                                print(message.body_markdown)
                                print("Replying to", mail.authors, "about valid Steam IDs. Archiving.")
                                continue

                        Invalid = re.search(r'(?i)invalid', message.body_markdown)
                        if Invalid is not None and Steam is not None:
                            mail.reply("The most common reason a Steam ID is not detected is due to a typo. Try clicking your link and confirming it takes you to your profile. \n\nOccasionally, Steam's servers don't load profiles properly and if the profile is unable to load it is considered invalid. Please try posting again if you're confident all else is in order. \n\nSee our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules) and [FAQ](https://www.reddit.com/r/GiftofGames/wiki/index#wiki_giftofgames_faq) for more information. \n\nThis message was sent by a bot. Please reply if it did not answer your question and a human will reply in about 48 hours.")
                            mail.archive()
##                            print(message.body_markdown)
                            print("Replying to", mail.authors, "about valid Steam IDs. Archiving.")
                            continue

                        ExposedKey = re.search(r'(?i)(?=.*?([A-Z]\d|\d[A-Z]))[A-Z0-9]{4,5}-[A-Z0-9]{4,5}-[A-Z0-9]{4,5}', message.body_markdown)
                        HumbleGift = re.search(r'(?i)gift\?key=', message.body_markdown)
                        FalsePositiveKey = re.search(r'(?i)(1234|ABCD|XYZ|XXX|http|.com|Switch|friend code)', message.body_markdown)
                        if ExposedKey is not None or HumbleGift is not None:
                            if FalsePositiveKey is None:
                                mail.reply("Please note, we currently do not accept games to gift on the sub. We have not redeemed your key and you may post your own offer or gift it to a friend. \n\nSee our [full rules](https://www.reddit.com/r/GiftofGames/wiki/rules) and [FAQ](https://www.reddit.com/r/GiftofGames/wiki/index#wiki_giftofgames_faq) for more information. \n\nThis message was sent by a bot. Please reply if it did not answer your question and a human will reply in about 48 hours.")
                                mail.archive()
##                                print(message.body_markdown)
                                print("Replying to", mail.authors, "that we don't accept key donations. Archiving.")
                                continue

                        # These last two are ones where another bot sends a user a message, and this bot cleans it up just to immediately archive it. No reply needed.
                        GOGReminder = re.search(r'(?i)As a reminder, all gifts received on this subreddit require you to post a \[GOG\] thank you thread', message.body_markdown)
                        if GOGReminder is not None:
                            mail.archive()
##                            print(message.body_markdown)
                            continue          

                        Cooldown = re.search(r'(?i)You have been put on a cooldown', message.body_markdown)
                        if Cooldown is not None:
                            mail.archive()
##                            print(message.body_markdown)
                            continue

                        CooldownRemover = re.search(r'(?i)Your cooldown has been removed', message.body_markdown)
                        if CooldownRemover is not None:
                            mail.archive()
##                            print(message.body_markdown)
                            continue
                        
    # Prints errors
    except Exception as e:
        print(e)
        time.sleep(3)
        continue
