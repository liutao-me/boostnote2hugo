import os
import shutil
import cson

boostnote_path = r"/Users/tao/Google Drive/sync/Boostnote/notes"
blog_path = r"/Users/tao/Work/mine/blog"
posts_path = blog_path + "/content/posts"
local_public_path = blog_path + '/public'
line_break = "\n"


def generate_posts_from_boostnote():
    os.chdir(boostnote_path)

    for file in os.listdir(boostnote_path):

        # 忽略后缀名不是 .cson  的文件
        if file[-5:] != '.cson':
            continue

        #  文章信息，默认作者、email
        #  没有记录时间的，统一按 2019-10-01 处理
        post_info = {
            'title': "",
            'author': "Liu Tao",
            'email': "i@liutao.me",
            'date': "2019-10-01",
            'export_file_name': "",
            'content': ""
        }
        with open(file, 'r') as fin:
            obj = cson.load(fin)
            if "publicBlog" in obj['tags']:
                post_info['title'] = obj['title']
                # 判断 info 信息是否已获取完成
                is_info_completed = False

                for line in obj["content"].split(sep=line_break):
                    if line.startswith('#+') and not is_info_completed:
                        print(line)
                        meta = line[2:].split(':')
                        post_info[meta[0].lower()] = meta[1].strip()
                        continue

                    #  此处不要标题，因为已经取到标题了
                    if line.startswith('# '):
                        # info 信息已取完整，那么后面碰到 #+ 的内容就不会再去解析
                        # 因为代码块中有 #+
                        is_info_completed = True
                        continue

                    post_info["content"] += line + line_break

        # 没有短链接的，不处理
        if post_info['export_file_name'] == "":
            continue

        # 新的博客地址
        blog_file = os.path.join(posts_path, post_info['export_file_name'] + '.md')
        print('prepare to generate new post')
        print(post_info['title'])
        print(file)
        print(blog_file)
        with open(blog_file, 'w') as file_object:
            file_object.write("---" + line_break)
            file_object.write('title: "' + post_info['title'] + '"' + line_break)
            file_object.write("date: " + post_info['date'] + line_break)
            file_object.write('draft: false' + line_break)

            # ananke 主题模板中的分享变量
            file_object.write('disable_share: true' + line_break)

            file_object.write("---" + line_break)
            file_object.write(post_info['content'])


def exec_github_commands():
    os.chdir(blog_path)

    for cmd in ['rm -rf public', 'gsed -i \'1c base = "https://liutao.me"\' config.toml ', 'hugo', ]:
        exec_cmd(cmd)

    os.chdir(local_public_path)

    cmds = [
        'echo "liutao.me" > CNAME',
        'git init',
        'git remote add origin liutao-me.github.com:liutao-me/liutao-me.github.io.git',
        'git add .',
        'git commit -m "publish posts"',
        'git push -f origin master',
    ]

    for cmd in cmds:
        exec_cmd(cmd)


def exec_gitee_commands():
    os.chdir(blog_path)

    for cmd in ['rm -rf public', 'gsed -i \'1c base = "https://liutao-me.gitee.io"\' config.toml ', 'hugo', ]:
        exec_cmd(cmd)

    os.chdir(local_public_path)

    cmds = [
        'git init',
        'git remote add gitee git@gitee.com:liutao-me/liutao-me.git',
        'git add .',
        'git commit -m "publish posts"',
        'git push -f gitee master',
    ]

    for cmd in cmds:
        exec_cmd(cmd)


# 使用 git 管理，然后发布
def use_git_and_push():
    os.chdir(blog_path)

    cmds = [
        'git checkout develop',
        'git add .',
        'git commit -m "auto import posts from boostnote"',
    ]
    for cmd in cmds:
        exec_cmd(cmd)

    exec_gitee_commands()
    exec_github_commands()


# 执行命令
def exec_cmd(cmd):
    print('current command: ' + cmd)
    print(os.system(cmd))


# 清空目录
def empty_dir(path):
    for f in os.listdir(path):
        filepath = os.path.join(path, f)
        if os.path.isfile(filepath):
            os.remove(filepath)
            print(str(filepath) + " removed!")
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath, True)
            print("dir " + str(filepath) + " removed!")


if __name__ == '__main__':
    # 清空 content/posts 目录
    empty_dir(posts_path)

    # boostnote 迁移到 hugo
    generate_posts_from_boostnote()

    # git 管理，并上传
    use_git_and_push()

    print('Congratulations， everything is OK!')
