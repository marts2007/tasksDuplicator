import http_fetcher as ht
import logger
import json
class Graph():

    def __init__(self,code='',refresh_token='',params={}) -> None:
        self.tenant_id = params['tenant_id']
        self.client_id = params['client_id']
        self.group_id = params['group_id']
        self.secret = params['secret']
        self.token = None
        self.refresh_token = params['refresh_token']
        self.SCOPES = params['SCOPES']
        if code:
            self.get_refresh_token(code)
        if refresh_token:
            self.refresh_token=refresh_token
        self.check_token()
        print(self.refresh_token)

    def get_refresh_token(self, code='', redirect_url='http://localhost/setcode'):
        url = 'https://login.microsoftonline.com/{}/oauth2/v2.0/token'.format(
            self.tenant_id)


        params = {
            'client_id': self.client_id,
            'scope': self.SCOPES,
            'redirect_uri': redirect_url,

           #  'client_secret': config.secret
        }
        if not code:
            logger.log('updating token by refresh_token')
            params['refresh_token']=self.refresh_token
            params['grant_type']='refresh_token'
        else:
            logger.log('updating token by code')
            params['code']=code
            params['grant_type']='authorization_code'
        response = ht.request(url, params)
        if 'refresh_token' in response:
            logger.log('we got new refresh_token')
            self.refresh_token= response['refresh_token']
        if 'access_token' in response:
            logger.log('we got new access_token')
            self.token= response['access_token']
            return True
        return False

    def update_token(self):
        if self.refresh_token:
            logger.log('we have refresh_token, let`s try to update token')
            if self.get_refresh_token():
                return True
        return False


    def check_token(self):
        logger.log('checking token')
        if self.token:
            response = ht.request('https://graph.microsoft.com/v1.0/me', headers={
            'Authorization': 'Bearer {}'.format(self.token)})
            if not 'error' in response:
                logger.log('Token works')
                return True
        logger.log('token is empty or invalid')
        if (self.update_token()):
            return self.refresh_token
        return False

    def get_me(self):
        response = self.request('/me')
        return response

    def get_groups(self):
        response = self.request('/groups/'.format(self.group_id))
        return response

    def get_plans(self,group_id):
        response = self.request('/groups/{}/planner/plans'.format(group_id))
        return response

    def get_tasks(self,plan_id):
        response = self.request('/planner/plans/{}/tasks'.format(plan_id))
        return response

    def create_task(self,task):
        response = self.request('/planner/tasks',method='post',json=task)
        return response

    def request(self, url='', params={},headers={}, method='get',json=None):
        if self.check_token():
            response = ht.request('https://graph.microsoft.com/v1.0/{}'.format(url), headers={
                'Authorization': 'Bearer {}'.format(self.token)},param=params,json=json,method=method)
            return response
        pass

