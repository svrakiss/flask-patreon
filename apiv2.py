from patreon import API;
from patreon.jsonapi.url_util import build_url
import requests
from patreon.utils import user_agent_string
from patreon.jsonapi.parser import JSONAPIParser

# I'm adding some of the API v2 endpoints here
class API2(API):
    def __init__(self, access_token):
        super(API2, self).__init__(access_token)

    def fetch_patron_by_id(self,member_id,includes=None,fields=None):
        return self.__get_jsonapi_doc2(
            build_url('v2/members/{0}'.format(member_id),includes=includes,fields=fields)
        )

    def fetch_campaign_patrons(self,campaign_id, includes=None,fields=None):
        return self.__get_jsonapi_doc2(
            build_url(
                'v2/campaigns/{0}/members'.format(campaign_id), includes=includes, fields=fields
            )
        )

    def __get_jsonapi_doc2(self, suffix):
        response_json = self.__get_json2(suffix)
        if response_json.get('errors'):
            return response_json
        return JSONAPIParser(response_json)

    def __get_json2(self, suffix):
        response = requests.get(
            "https://www.patreon.com/api/oauth2/{}".format(suffix),
            headers={
                'Authorization': "Bearer {}".format(self.access_token),
                'User-Agent': user_agent_string(),
            }
        )
        return response.json()