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
    tokens = oauth_client.get_tokens(request.values.get('code'), REDIRECT_URI)
    return tokens

@app.route('/')
def homepage():
	return "Hi"

@app.route('/member/',methods=['GET'])
def find_by_discord_id():
    discord_id=request.values.get('discord_id',None)
    patron_id=request.values.get('patron_id',None)
    campaign_id=request.values.get('campaign_id',None)
    if(request.is_json):
        includes=request.json.get('include',[])
        fields = request.json.get('fields',{})
        if(len(includes) == 0):
            includes=['currently_entitled_tiers']
        if(len(fields)==0 or not isinstance(fields,dict)):
            fields={
                'member':['full_name','patron_status'],'tier':['title','discord_role_ids']}
    else:
        includes=['currently_entitled_tiers']
        fields={'member':['full_name','patron_status'],'tier':['title','discord_role_ids']}
    if(patron_id is not None):
        if(request.is_json):
            return find_by_patron_id(patron_id,includes=includes,fields=fields);
        else:
            return find_by_patron_id(patron_id=patron_id);
    else:
        includes = set(includes)
        includes.add('user')
        fields.update({'user':set(fields.get('user',{}))})
        fields.get('user').add('social_connections')

    grab_discord_id = lambda x: x.attribute('social_connections').get('discord').get('user_id',None)
    has_discord = lambda x: x.attribute('social_connections').get('discord') is not None;
    access_token = app.config.get('TOKENS')['access_token']
    api_client = API2(access_token)

    if(discord_id is not None):
        if(campaign_id is not None):
            # campaign_members = api_client.fetch_campaign_patrons(campaign_id=campaign_id,includes=['currently_entitled_tiers','user'],fields={
        #    'member':['full_name','patron_status'],'tier':['title','discord_role_ids'],'user':['social_connections']})
            campaigns_iter=(campaign_id)
        else:
            # campaign_members=api_client.fetch_campaign_v2(includes=request.json.get('include',None),fields=request.json.get('fields',None))
            campaigns = api_client.get_campaigns(10)
            campaigns_iter = (x.id() for x in campaigns.data())
        member_cursor=None

        for campaign in campaigns_iter:
                
            while True:
                campaign_members=api_client.get_campaigns_by_id_members(campaign,request.values.get('page_size',100),cursor=member_cursor,includes=includes,fields=fields)
                for x in campaign_members.data():
                    if(has_discord(x.relationship('user')) and discord_id ==grab_discord_id(x.relationship('user'))):
                        return x.json_data;
                # answer=more-itertools.first_true(campaign_members.data(),default=None,pred=lambda x: has_discord(x.relationship('user')) and discord_id ==grab_discord_id(x.relationship('user')))
                # if(answer is not None):
                #     return answer.json_data;
                # if the default page size for grabbing members was enough
                if('links' not in campaign_members.json_data):
                    break;
                else:
                    try:
                        member_cursor=api_client.extract_cursor(campaign_members)
                    except:
                        break;

        return 'Cannot find member';
    return 'Cannot find member';
    
def find_by_patron_id(patron_id,includes=['currently_entitled_tiers'],fields={'tier':['title','description'],'member':['full_name','patron_status']}):
    access_token = app.config.get('TOKENS')['access_token']
    api_client = API2(access_token)
    member_response=api_client.fetch_patron_by_id(member_id=patron_id,includes=includes,fields=fields)

    return member_response.data().json_data


@app.route('/campaign/members')
def get_campaign_members():
    access_token = app.config.get('TOKENS')['access_token']
    api_client = API2(access_token)
    if request.is_json:
        member_response = api_client.fetch_campaign_patrons(campaign_id=request.values.get('campaign_id'),includes=request.json.get('include',None)
        ,fields=request.json.get('fields',None));
    else:
        member_response = api_client.fetch_campaign_patrons(campaign_id=request.values.get('campaign_id'))
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
