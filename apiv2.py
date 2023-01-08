from patreon import API;
from patreon.jsonapi.url_util import build_url
import requests
from patreon.utils import user_agent_string
from patreon.jsonapi.parser import JSONAPIParser
from typing import Iterable
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
    
    def fetch_campaign_v2(self,includes=None,fields=None):
        return self.__get_jsonapi_doc2(
            build_url(
                'v2/campaigns', includes=includes, fields=fields
            )
        )


    def create_webhook(self,triggers:Iterable[str],uri:str,campaign_id:str):
        return self.__post_jsonapi_doc(
            build_url(
                'v2/webhooks'
            ),
            {"data":{
                "type":"webhook",
                "attributes":{
                    "triggers": [x for x in triggers],
                    "uri":uri
                },
             "relationships":{
                "campaign":{
                    "data":{
                        "type":"campaign",
                        "id":campaign_id
                    }
                }
             }
            }
            }
        )
    
    def __post_jsonapi_doc(self,suffix,body):
        response_json = self.__post_json(suffix,body)
        if response_json.get('errors') is not None:
            return response_json;
        return JSONAPIParser(response_json)

    def __post_json(self, suffix,body):
        response = requests.post(
            "https://www.patreon.com/api/oauth2/{}".format(suffix),
            headers={
                'Authorization':"Bearer {}".format(self.access_token),
                'User-Agent':user_agent_string()
            },
            json=body
        )
        return response.json()

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