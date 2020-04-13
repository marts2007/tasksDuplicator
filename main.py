from logger import log
from config import config
from graph import Graph

from flask import Flask, request, redirect, session, render_template

app = Flask(__name__)
app.secret_key = b'_5#y2L"F432Q8ssasaz\n\xec]/'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

@app.route('/test')
def test():
    return render_template("index.html")

@app.route('/')
@app.route('/postTasks')
def index():
    tvars={}
    if 'fullname' in session:
        tvars['fullname']=session['fullname']
    else:
        tvars['fullname']=None
    if not 'refresh_token' in session:
        return render_template("login.html",tvars=tvars,url=getCode())
    if session['refresh_token'] == None:
        return render_template("login.html",tvars=tvars,url=getCode())
        # there is no refresh_token - so let`s get it
    graph = Graph(refresh_token=session['refresh_token'],
                  params=config.get_dict())
    response = graph.get_me()
    if not 'id' in response:
        tvars["text"]="Can`t login"
        return render_template("error.html",tvars=tvars)

    my_id = response['id']

    session['fullname'] = response['displayName']
    tvars['fullname']=session['fullname']
    if request.path !='/postTasks':
        return render_template('index.html',tvars=tvars)



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
            tvars["text"] =  'Sorry there is no tasks for user {}'.format(
                config.plan_copy_user_id)
            return render_template("error.html", tvars=tvars)
        tvars['success_title']="Done!"
        tvars['text']='Your tasks has been created! ({})'.format(len(tasks))
        return render_template("success.html", tvars=tvars)
    if 'error' in response:
        tvars["text"]=response['error']['message']
        return render_template("error.html",tvars=tvars)
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
    return url


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
