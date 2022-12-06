import patreon
from flask import request
from __init__ import app;
from apiv2 import API2;
creator_id = None     # Replace with your data
REDIRECT_URI = "http://localhost:65010/v2/oauth/redirect"
@app.route('/v2/oauth/redirect',endpoint='xxxx',methods=['GET','POST'])
def oauth_redirect():
    oauth_client = patreon.OAuth(app.config['CLIENT_ID'], app.config['CLIENT_SECRET'])
    tokens = oauth_client.get_tokens(request.values.get('code'), REDIRECT_URI)
    access_token = tokens.get('access_token',None)
    if (access_token is None):
        return 'Denied';
    api_client = patreon.API(access_token)
    # user_response = api_client.fetch_user()
    # user = user_response.data()
    # pledges = user.relationship('pledges')
    return 'Hey'

@app.route('/gimme_token',methods=['POST'])
def auth_resource():
    oauth_client = patreon.OAuth(app.config['CLIENT_ID'], app.config['CLIENT_SECRET'])
    # request.
    tokens = oauth_client.get_tokens(request.values.get('code'), REDIRECT_URI)
    return tokens

# @app.route('/')
# def homepage():
# 	text = '<a href="%s">Authenticate with reddit</a>'
# 	return text % make_authorization_url()

@app.route('/member/',methods=['GET'])
def find_by_discord_id():
    discord_id=request.values.get('discord_id','None')
    patron_id=request.values.get('patron_id','None')
    if(patron_id is not None):
        return find_by_patron_id(patron_id,includes=request.values.get('include',None)
    ,fields=request.values.get('fields',None));
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
    
def find_by_patron_id(patron_id,includes=None,fields=None):
    access_token = app.config.get('TOKENS')['access_token']
    api_client = API2(access_token)
    member_response=api_client.fetch_patron_by_id(member_id=patron_id,includes=includes,fields=fields)

    return member_response.data().json_data

@app.route('/campaign/members')
def get_campaign_members():
    access_token = app.config.get('TOKENS')['access_token']
    api_client = API2(access_token)
    member_response = api_client.fetch_campaign_patrons(campaign_id=request.values.get('campaign_id'),includes=request.values.get('include',None)
    ,fields=request.values.get('fields',None));
    return [x.json_data for x in member_response.data()]


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
