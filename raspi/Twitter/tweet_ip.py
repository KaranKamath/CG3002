import tweepy
import utils

auth = tweepy.OAuthHandler('3r8XaB3DrVihMoCjqbvAcu6xZ', 'QYjJ6ezrFDwU2UcHCrLUvQvnbZc6NQcWZiPP0yq1A57xXc5Edp')
auth.set_access_token('3535282152-vdd0chrSNOYI61xHa3oC62rxwrnZvWUIhZJCy0t', 'yOgsiiYXPIKHTEvcsy98u9MdXld28yDAfaN8layJa3xdE')

api = tweepy.API(auth)

current_IP = utils.get_IP()

if current_IP != utils.get_last_IP():
    status = api.update_status(status='My NUS IP is ' + current_IP)

    utils.write_current_IP()
