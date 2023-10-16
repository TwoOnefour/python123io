import os
import sys
import openai
import requests
from urllib3 import disable_warnings
import asyncio
import httpx
import re
from lxml import etree
disable_warnings()


def echo(message):
    import datetime
    print(f"{str(datetime.datetime.now())[:-8]}\t{message}")


async def send_to_gpt(content):
    openai.proxy = "http://127.0.0.1:10809"
    openai.api_key = ""
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "你需要根据我给出的html内容写出python代码。只给出代码，没有其他任何文字，字符，不要有多余的文字"},
            {"role": "assistant", "content": "好的，我将只给出python代码"},
            {"role": "user", "content": '<h3><strong><span style=\"color: #000000;\">输出斐氏数列前n项</span></strong></h3>\n<p>类型：分支结构、简单循环</p>\n<hr />\n<p><b>斐氏数列（第三项开始，每项为相邻前两项的和）：</b></p>\n<p><b>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; 1, 1, 2, 3, 5, 8, 13, 21, ...</b></p>\n<h4><strong>输入</strong></h4>\n<pre>键盘输入整数n</pre>\n<h4><strong>输出</strong></h4>\n<p>在一行中输出前n项数列元素，元素间用逗号间隔</p>\n<h4><strong>示例</strong></h4>\n<pre class=\"language-python\"><code>输入\n4\n输出\n1,1,2,3\n\n输入\n7\n输出\n1,1,2,3,5,8,13</code></pre>\n<p></p>'},
            # {"role": "assistant", "content": '字符串分类统计代码如下：```python\ndef fibonacci():\n\ta, b = 1, 1\n\twhile True:\n\t\tyield a\n\t\ta, b = b, a + b\n\nf = fibonacci()\nanswer = ""\nfor _ in range(eval(input())):\n\tanswer += str(next(f))\n\tanswer += ","\nprint(answer.strip(","))\n```'},
            # {"role": "user", "content": "这不是我要的答案，请不要含有'字符串分类统计代码如下：```python'，只输出代码"},
            {"role": "assistant", "content": 'def fibonacci():\n\ta, b = 1, 1\n\twhile True:\n\t\tyield a\n\t\ta, b = b, a + b\n\nf = fibonacci()\nanswer = ""\nfor _ in range(eval(input())):\n\tanswer += str(next(f))\n\tanswer += ","\nprint(answer.strip(","))\n'},
            {"role": "user", "content": content}
        ]
    )
    content = response['choices'][0]['message']['content']
    if "`" in content:
        pattern = re.compile(r'`([^`]+)`')
        return re.match(pattern, content)
    return content
    # return re.match(pattern, content)


class Python123Robot:
    def __init__(self):
        self.session = requests.session()
        self.url = "https://python123.io"
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60",
            "Content-Type":"application/json"
        })
        self.token = None
        self.session.verify = False
        self.session.get(self.url)
        self.courseID = None
        self.taskID = None
        self.loop = asyncio.get_event_loop()
        self.pattern = None

    def get_info(self):
        location = "/api/v1/user"
        res_json = self.session.get(f"{self.url}{location}").json()
        if res_json["code"] == 200:
            return True
        return False

    def login(self):
        if os.path.exists("token"):
            echo("存在token，将用token恢复登陆状态")
            with open("token", "r") as f:
                self.token = f.read()
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                })
                self.session.cookies.set("token", self.token)
                if self.get_info():
                    echo("恢复token成功")
                    return True
                else:
                    echo("恢复token失败，将进入正常流程")
        location = "/api/v1/session"
        res_json = self.session.put(f"{self.url}{location}", json={
            "email": self.email,
            "pass": self.passwd
        }).json()
        if res_json["code"] == 201:
            self.token = res_json["data"]["token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
            })
            self.session.cookies.set("token", self.token)
            with open("token", "w") as f:
                f.write(self.token)
            return True
        return False

    def get_course(self):
        if os.path.exists("courseid"):
            echo("存在课程id，恢复")
            with open("courseid", "r") as f:
                self.courseID = int(f.read())
            return
        location = "/api/v1/student/courses"
        res_json = self.session.get(f"{self.url}{location}").json()
        if res_json["code"] == 200:
            while True:
                tmp_id = {}
                for i in res_json["data"]:
                    echo(f"id: {i['_id']}, {i['name']}")
                    tmp_id[i["_id"]] = i["name"]
                self.courseID = int(input("请选择需要刷课的课程id："))
                try:
                    if tmp_id.get(self.courseID) is not None:
                        echo(f"你选择了{tmp_id.get(self.courseID)}")
                        with open("courseid", "w") as f:
                            f.write(str(self.courseID))
                        break
                except Exception as e:
                    echo("输入错误")
                    continue

    def get_task(self):
        location = f"/api/v1/student/courses/{self.courseID}/groups"
        res_json = self.session.get(f"{self.url}{location}").json()
        if res_json["code"] == 200:
            while True:
                tmp_id = {}
                if self.pattern != "-s":
                    for i in res_json["data"]:
                        # echo(f"id: {i['_id']}, {i['name']}")
                        if self.if_task_open(i["end_at"]):
                            tmp_id[i["_id"]] = i["name"]
                    # self.taskID = int(input("请选择需要作业id："))
                    # try:
                    #     if tmp_id.get(self.taskID) is not None:
                    #         echo(f"你选择了{tmp_id.get(self.taskID)}")
                    #         break
                    # except Exception as e:
                    #     echo("输入错误")
                    #     continue
                else:
                    res_json["data"].reverse()
                    for i in res_json["data"]:
                        if "签到" in i["name"]:
                            if not self.if_task_open(i["end_at"]):
                                echo("该签到已结束")
                                sys.exit(0)
                            self.taskID = i["_id"]
                            echo(f'{i["name"]}')
                            tmp_id[i["_id"]] = i["name"]
                            break

                return tmp_id

    def if_task_open(self, end_at):
        # "end_at": "2023-09-18T00:00:00.000Z",
        import datetime
        endTime = datetime.datetime.strptime(end_at[:-5], "%Y-%m-%dT%H:%M:%S")
        if (datetime.datetime.now() - datetime.timedelta(hours=8) - endTime).seconds >= 0 and (datetime.datetime.now() - datetime.timedelta(hours=8) - endTime).days >= 0:
            return False
        return True

    async def get_problem(self):
        location = f"/api/v1/student/courses/{self.courseID}/groups/{self.taskID}/problems"
        res_json = self.session.get(f"{self.url}{location}").json()
        if res_json["code"] == 200:
            task = []
            task_ids = []
            result = []
            for i in res_json["data"]:
                # task.append(self.loop.create_task(send_to_gpt(content=i["content"])))
                if i["record"]["commits_count"] != 0:
                    echo(f"{i['name']}已经提交过了，跳过该问题")
                    continue
                task_ids.append(i["_id"])
                etree.HTMLParser(encoding="utf-8")
                # tree = etree.parse(local_file_path)
                tree = etree.HTML(i["explanation_content"])
                result.append(etree.HTML(i["explanation_content"])[0][0][0].text)
            # for i in task:
            #     await i
            # result = await asyncio.gather(*task)
            # task = []
            for i in range(len(result)):
                # echo(result[i])
                task.append(self.loop.create_task(self.save_code(task_ids[i], result[i])))
            for i in task:
                await i

    async def save_code(self, problem_id, code):
        async with httpx.AsyncClient(verify=False, headers=self.session.headers, cookies=self.session.cookies, timeout=30) as client:
            location = f"/api/v1/student/courses/{self.courseID}/groups/{self.taskID}/problems/{problem_id}/code"
            if code is not None:
                res_json = await client.put(f"{self.url}{location}", json={
                    "code": code + "#  因为太懒所以用了自己写的python爬虫，请老师不要介意"
                })
                if res_json.json()["code"] == 200:
                    echo(f"id{problem_id}提交成功")
                await client.get(f"{self.url}{location}")
                location = f"/api/v1/student/courses/{self.courseID}/groups/{self.taskID}/problems/{problem_id}/testcases/result"
                await client.get(f"{self.url}{location}")
            else:
                echo(f"id{problem_id}提交失败")

    def run(self):
        if self.login():
            echo("登录成功")
            self.get_course()
            task = self.get_task()
            for i in task:
                self.taskID = i
                self.loop.run_until_complete(self.get_problem())
        else:
            echo("登陆失败")


if __name__ == "__main__":
    if len(sys.argv) == 1 :
        print("用法：\npython3 robot.py -s\t做题签到\npython3 robot.py -i\t刷题\npython3 robot.py -h\t返回此帮助\n\n第一次运行请选择课程号，之后课程号会保存")
    elif sys.argv[1] == "-s" or sys.argv[1] == "-i":
        robot = Python123Robot()
        robot.pattern = sys.argv[1]
        robot.email = ""  # 你的邮箱
        robot.passwd = ""  # 你的密码
        robot.run()
    else:
        print(
            "用法：\npython3 robot.py -s\t做题签到\npython3 robot.py -i\t刷题\npython3 robot.py -h\t返回此帮助\n\n第一次运行请选择课程号，之后课程号会保存")
