import patreon
from flask import request
from __init__ import app;

creator_id = None     # Replace with your data
REDIRECT_URI = "http://localhost:65010/v2/oauth/redirect"
# @app.route('/v2/oauth/redirect',endpoint='xxxx' )
# def oauth_redirect():
#     oauth_client = patreon.OAuth(client_id, client_secret)
#     tokens = oauth_client.get_tokens(request.args.get('code'), '/v2/oauth/redirect')
#     access_token = tokens['access_token']

#     api_client = patreon.API(access_token)
#     user_response = api_client.fetch_user()
#     user = user_response.data()
#     pledges = user.relationship('pled ges')
#     pledge = pledges[0] if pledges and len(pledges) > 0 else None
#     print(pledge)
# @app.route('/')
# def homepage():
# 	text = '<a href="%s">Authenticate with reddit</a>'
# 	return text % make_authorization_url()

@app.route('/member/',methods=['GET'])
def find_by_discord_id():
    discord_id=request.args.get('discord_id')
    patron_id=request.args.get('patron_id')

    grab_discord_id = lambda x: x.attribute('social_connections').get('discord').get('user_id',None)

    access_token = app.config.get('TOKENS')['access_token']
    api_client = patreon.API(access_token)
    user_response = api_client.fetch_user()
    user = user_response.data()
    pledges = user.relationship('pledges')
    if(discord_id is not None):
        for x in pledges:
            if(discord_id ==grab_discord_id(x.relationship('patron'))):
                return x.attributes()
        return 'Nope';
    return 'Nope';
    
            
    

def make_authorization_url():
	# Generate a random string for the state parameter
	# Save it for use later to prevent xsrf attacks
	from uuid import uuid4;
	state = str(uuid4())
	save_created_state(state)
	params = {"client_id": CLIENT_ID,
			  "response_type": "code",
			  "state": state,
			  "redirect_uri": REDIRECT_URI,
			  "duration": "temporary",
			  "scope": "identity"}
	return 34

def save_created_state(state):
	pass
def is_valid_state(state):
	return True

if __name__ == '__main__':
	app.run(debug=True, port=65010)