from logger import log
from config import config
from graph import Graph

from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = b'_5#y2L"F432Q8ssasaz\n\xec]/'


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/plans')
def get_plans():
    if not 'refresh_token' in session:
        return getCode()
    if session['refresh_token'] == None:
        return getCode()
        # there is no refresh_token - so let`s get it
    graph = Graph(refresh_token=session['refresh_token'],
                  params=config.get_dict())
    response = graph.get_me()
    response2 = graph.get_plans(config.group_id)
    response3 = graph.get_tasks(config.plan_id)
    raise Exception(response, response2, response3)


@app.route('/')
def index():
    if not 'refresh_token' in session:
        return getCode()
    if session['refresh_token'] == None:
        return getCode()
        # there is no refresh_token - so let`s get it
    graph = Graph(refresh_token=session['refresh_token'],
                  params=config.get_dict())
    response = graph.get_me()
    if not 'id' in response:
        return response
    my_id = response['id']
    response = graph.get_tasks(config.plan_id)
    if 'value' in response:
        tasks = {}
        for task in response['value']:
            if config.plan_copy_user_id in task['assignments']:
                tmp_task = {
                    "planId": task['planId'],
                    "bucketId": task['bucketId'],
                    "title": task['title'],
                    "assignments": {
                        my_id: {
                            "@odata.type": "#microsoft.graph.plannerAssignment",
                            "orderHint": " !"
                        }
                    },
                }
                graph.create_task(tmp_task)
                tasks[task['id']] = task
        if len(tasks) == 0:
            return 'Sorry there is no tasks for user {}'.format(
                config.plan_copy_user_id)
        return 'Your tasks has been created! ({})'.format(len(tasks))

    raise Exception(response)


def getCode():
    log('getting code')
    url = \
        "https://login.microsoftonline.com/{}/oauth2/v2.0/authorize?" \
        "client_id={}" \
        "&response_type=code" \
        "&redirect_uri=http://localhost/setcode" \
        "&response_mode=query" \
        "&scope={}" \
        "&state=auth".format(config.tenant_id, config.client_id, config.SCOPES)
    return redirect(url, code=302)


@app.route('/setcode')
def setCode():
    if 'error_description' in request.args:
        return request.args.get('error_description')
    code = request.args.get('code')
    gr = Graph(code=code, params=config.get_dict())
    refresh_token = gr.refresh_token
    if not refresh_token or refresh_token == False:
        redirect('/logout', code=302)
    session['refresh_token'] = refresh_token
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
