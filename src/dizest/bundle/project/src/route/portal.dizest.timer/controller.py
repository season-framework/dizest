import season
from crontab import CronTab
from urllib import parse

Kernel = wiz.model("portal/dizest/kernel")
config = wiz.model("portal/dizest/config")

segment = wiz.request.match("/api/dizest/timer/<zone>/<path:path>")
zone = segment.zone
action = segment.path
workflow_id = wiz.request.query("workflow_id", True)

if config.acl(wiz, zone) == False:
    wiz.response.status(401)

user_id = config.user_id(wiz, zone)

if action == 'list':
    try:
        res = []
        cron  = CronTab(user=user_id)
        for job in cron:
            time = " ".join([str(x) for x in job.slices])
            comment = job.comment.split(";")
            cron_id = comment[0]
            if cron_id == workflow_id:
                comment = ";".join(comment[1:])
                res.append(dict(comment=comment, time=time))
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200, res)

if action == 'remove':
    try:
        comment = wiz.request.query("comment", True)
        comment = f"{workflow_id};{comment}"
        cron  = CronTab(user=user_id)
        rows = cron.find_comment(comment)
        for job in rows:
            job.enable(False)
            cron.remove(job)
        cron.write()
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200)

if action == 'add':
    try:
        cwd = config.cwd(wiz, zone, workflow_id)
        host = config.cron_uri(wiz, zone, workflow_id)
        host = f"{host}/api/dizest/cron/start"

        comment = wiz.request.query("comment", True)
        comment = f"{workflow_id};{comment}"

        time = wiz.request.query("time", True)
        spec = wiz.request.query("spec", True)

        query = dict()
        query['zone'] = zone
        query['workflow_id'] = workflow_id
        query['spec'] = spec
        query['user'] = user_id
        query = parse.urlencode(query, encoding='UTF-8', doseq=False)

        command = f'curl "{host}?{query}"'

        cron  = CronTab(user=user_id)
        job = cron.new(command=command, comment=comment)
        job.setall(time)
        cron.write()
        job.enable()
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200)

wiz.response.status(404)