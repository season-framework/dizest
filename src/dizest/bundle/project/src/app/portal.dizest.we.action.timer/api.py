from crontab import CronTab

config = wiz.model("portal/dizest/config")
KernelClass = wiz.model("portal/dizest/kernel")

kernel_id = config.kernel_id()
user_id = config.user()
cwd = config.cwd()
namespace = wiz.request.query("namespace", True)
workflow_id = wiz.request.query("workflow_id", True)

def binder(path):
    segment = wiz.request.match(f"/dizest/timer/{path}")
    if segment is not None:
        return True
    return False

def list():
    try:
        res = []
        cron  = CronTab(user=user_id)
        for job in cron:
            time = " ".join([str(x) for x in job.slices])
            comment = job.comment.split(";")
            cron_namespace = comment[0]
            if cron_namespace == namespace:
                comment = ";".join(comment[1:])
                res.append(dict(comment=comment, time=time))
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200, res)

def remove():
    try:
        comment = wiz.request.query("comment", True)
        comment = f"{namespace};{comment}"
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
        host = config.cronhost()
        host = f"{host}/dizest/api/cron"

        comment = wiz.request.query("comment", True)
        comment = f"{namespace};{comment}"

        time = wiz.request.query("time", True)
        spec = wiz.request.query("spec", True)

        command = f'curl "{host}?id={kernel_id}&namespace={namespace}&workflow_id={workflow_id}&spec={spec}&user={user_id}&cwd={cwd}"'

        cron  = CronTab(user=user_id)
        job = cron.new(command=command, comment=comment)
        job.setall(time)
        cron.write()
        job.enable()
    except Exception as e:
        print(e)
        wiz.response.status(500, e)
    wiz.response.status(200)
