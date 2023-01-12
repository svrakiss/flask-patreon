import patreon
from flask import request, jsonify
from __init__ import app;
from apiv2 import API2;
from patreon.jsonapi.parser import JSONAPIParser, JSONAPIResource
import itertools
import logging
import datetime
import awsgi
_log = logging.getLogger(__name__)
_log.setLevel(level=10)

REDIRECT_URI = "http://localhost:65010/v2/oauth/redirect"
@app.route('/v2/oauth/redirect',endpoint='xxxx',methods=['GET','POST'])
def oauth_redirect():
    oauth_client = patreon.OAuth(app.config['CLIENT_ID'], app.config['CLIENT_SECRET'])
    tokens = oauth_client.get_tokens(request.values.get('code'), REDIRECT_URI)
    access_token = tokens.get('access_token',None)
    if (access_token is None):
        return 'Denied';
    api_client = patreon.API(access_token)
    return 'Hey'

@app.route('/gimme_token',methods=['POST'])
def auth_resource():
    oauth_client = patreon.OAuth(app.config['CLIENT_ID'], app.config['CLIENT_SECRET'])
    tokens = oauth_client.get_tokens(request.values.get('code'), REDIRECT_URI)
    return tokens

@app.route('/')
def homepage():
	return "Hi"

@app.route('/member/',methods=['GET','POST'])
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
    access_token = grab_token()
    api_client = API2(access_token)

    if(discord_id is not None):
        if(campaign_id is not None):
            campaigns_iter=(campaign_id)
        else:
            campaigns = api_client.get_campaigns(10)
            if  not isinstance(campaigns,JSONAPIParser):
                return campaigns
            campaigns_iter = (x.id() for x in campaigns.data())
        member_cursor=None

        for campaign in campaigns_iter:
                
            while True:
                campaign_members=api_client.get_campaigns_by_id_members(campaign,request.values.get('page_size',100),cursor=member_cursor,includes=includes,fields=fields)
                for x in campaign_members.data():
                    if(x.relationship('user').attribute('social_connections') is None):
                        continue
                    if(has_discord(x.relationship('user')) and discord_id ==grab_discord_id(x.relationship('user'))):
                        return parseJSONAPI(x);
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
    access_token = grab_token()
    api_client = API2(access_token)
    member_response=api_client.fetch_patron_by_id(member_id=patron_id,includes=includes,fields=fields)
    if  not isinstance(member_response,JSONAPIParser):
        return member_response

    return parseJSONAPI(member_response.data())


@app.route('/campaign/members',methods=['GET','POST'])
def get_campaign_members():
    access_token = grab_token()
    # _log.info("yo1")
    print("why " +str(datetime.datetime.utcnow()))
    api_client = API2(access_token)
    if request.is_json:
        get_next =lambda cursor:  api_client.get_campaigns_by_id_members(request.values.get('campaign_id'),request.values.get('page_size',100), cursor=cursor, includes=request.json.get('include',None)
        ,fields=request.json.get('fields',None));
    else: 
        get_next =lambda cursor: api_client.get_campaigns_by_id_members(request.values.get('campaign_id'), request.values.get('page_size',100),cursor=cursor)
    member_response = get_next(None)
    if  not isinstance(member_response,JSONAPIParser):
        return member_response
    member_response = get_all_pages(member_response,get_next,api_client.extract_cursor)
    result =[ parseJSONAPI(x) for x in member_response]
    print(f'sending {str(len(result))}  items')
    return result

def get_all_pages(member_response:JSONAPIParser, get_next,extract_cursor):
    cursor = None
    all_responses = member_response.data()
    while True:
        if('links' not in member_response.json_data):
            return all_responses;
        try:
            cursor=extract_cursor(member_response)
        except:
            return all_responses;
        member_response = get_next(cursor)
        if not isinstance(member_response,JSONAPIParser):
            return all_responses;
        all_responses = itertools.chain(all_responses, member_response.data())
        

def parseJSONAPI(member:JSONAPIResource):
    patron = dict();
    grab_discord_id = lambda x: x.attribute('social_connections').get('discord').get('user_id',None)
    has_discord = lambda x: x.attribute('social_connections').get('discord') is not None;

    if(member.attribute("patron_status") is None):
        # this is probably the creator
        patron['status']="override"
    else:
        patron['status'] = member.attribute("patron_status")
        if(member.relationship("currently_entitled_tiers") is not None):
            if(len(member.relationship("currently_entitled_tiers"))>0):
                if(member.relationship("currently_entitled_tiers")[0].attribute('title') is not None):
                    patron['tier'] = [ x.attribute('title') for x in member.relationship("currently_entitled_tiers")]
                    # print(member.relationship("currently_entitled_tiers")[0].attribute('title'))
    if(member.relationship('user') is not None):
        if(member.relationship('user').attribute('social_connections') is not None):
            if(has_discord(member.relationship('user'))):
                patron['discordId'] = grab_discord_id(member.relationship('user'))

    if(member.attribute("full_name") is not None):
        patron['name'] = member.attribute("full_name")
    patron['id'] = "PATREON_" + member.id()
    patron['patronId']=member.id()
    patron['sortKey']="INFO"
    return patron;

@app.route('/webhook')
def create_webhook():
    token = grab_token();
    api = API2(token);
   
    response =api.create_webhook(request.json.get('triggers',['members:create','members:update']),request.json.get('uri','http://localhost:65010/webhook/callback')
    ,campaign_id=request.json.get('campaign_id','3793891'))
    if not isinstance(response,JSONAPIParser):
        return response;
    
    print(
response.data()
    )
    return response.json_data;

@app.route('/webhook/callback')
def webhook_callback():
    sign = request.headers.get('X-Patreon-Signature')
    print(sign)
    member =JSONAPIParser(request.json)

    result =  parseJSONAPI(member.data())
 # type: ignore
    print(result)
    return result
def grab_token():
    access_token = request.values.get('access_token',None)
    if(access_token is None):
        access_token = request.headers.get('Authorization', '').partition(' ')[2]
    # return app.config.get('TOKENS')['access_token']
    return access_token

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

def handler(event,context):
    return awsgi.response(app,event,context)
