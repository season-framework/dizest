from crontab import CronTab

zone = wiz.request.query("zone", True)
workflow_id = wiz.request.query("workflow_id", True)

def binder(path):
    segment = wiz.request.match(f"/dizest/timer/{path}")
    if segment is not None:
        return True
    return False

dconfig = wiz.model("portal/dizest/dconfig")

user_id = dconfig.user()
channel = dconfig.channel(zone=zone, workflow_id=workflow_id)

def list():
    try:
        res = []
        cron  = CronTab(user=user_id)
        for job in cron:
            time = " ".join([str(x) for x in job.slices])
            comment = job.comment.split(";")
            cron_namespace = comment[0]
            if cron_namespace == channel:
                comment = ";".join(comment[1:])
                res.append(dict(comment=comment, time=time))
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200, res)

def remove():
    try:
        comment = wiz.request.query("comment", True)
        comment = f"{channel};{comment}"
        cron  = CronTab(user=user_id)
        rows = cron.find_comment(comment)
        for job in rows:
            job.enable(False)
            cron.remove(job)
        cron.write()
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200)

def add():
    try:
        host = dconfig.cron_host()
        host = f"{host}/dizest/api/cron"

        comment = wiz.request.query("comment", True)
        comment = f"{channel};{comment}"

        time = wiz.request.query("time", True)
        spec = wiz.request.query("spec", True)

        command = f'curl "{host}?user={user_id}&kernel={spec}&zone={zone}&workflow_id={workflow_id}"'

        cron  = CronTab(user=user_id)
        job = cron.new(command=command, comment=comment)
        job.setall(time)
        cron.write()
        job.enable()
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200)
