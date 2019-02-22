from django.shortcuts import render
from login import models

from login import forms

# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings

# Create your views here.
import hashlib
import datetime
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user,)
    return code

def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = '来自www.liujiangblog.com的注册确认邮件'

    text_content = '''感谢注册www.liujiangblog.com，这里是刘江的博客和教程站点，专注于Python和Django技术的分享！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''
#20190222这个链接里面是href是原链接到一个网址http://127.0.0.1:8000（这个地址需要是一个外网地址，否则外网不能用）/confirm（进入url然后进入view）/?code={}"和code的具体数值
    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                    这里是刘江的博客和教程站点，专注于Python和Django技术的分享！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def hash_code(s, salt='mysite'):# 加点盐，rxq，gjh
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

def index(request):
    pass
    return render(request, 'login/index.html')
# def login(request):
#     if request.session.get('is_login',None):
#         return redirect("/index/")
#
#     if request.method == "POST":
#         # username = request.POST.get('username', None)
#         # password = request.POST.get('password', None)
#         login_form = forms.UserForm(request.POST)
#
#         message = "所有字段都必须填写！"
#         # if username and password:  # 确保用户名和密码都不为空
#         #     username = username.strip()
#         if login_form.is_valid():
#             username = login_form.cleaned_data['username']
#             password = login_form.cleaned_data['password']
#             # 用户名字符合法性验证
#             # 密码长度验证
#             # 更多的其它验证.....
#             try:
#                 user = models.User.objects.get(name=username)
#                 # if user.password == password:
#                 if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
#                     request.session['is_login'] = True
#                     request.session['user_id'] = user.id
#                     request.session['user_name'] = user.name
#                     return redirect('/index/')
#                 else:
#                     message = "密码不正确！"
#             except:
#                 message = "用户名不存在！"
#         # return render(request, 'login/login.html', {"message": message})
#         return render(request, 'login/login.html', locals())
#
#     login_form = forms.UserForm()
#     return render(request, 'login/login.html', locals())
#     # return render(request, 'login/login.html')
def login(request):
    if request.session.get('is_login', None):
#通过下面的if语句，我们不允许重复登录：这里应该登录的话-就返回到index页面不让重复登录。
        return redirect("/index/")

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
# message在login前端显示1，先检测验证码是否错误，错误会提示检查填写的内容2，如果验证码正确判断用户是否正确-错误用户不存在3，密码错误4，没有通过邮件
        if login_form.is_valid():
#每个Django表单的实例都有一个内置的is_valid()方法，用来验证接收的数据是否合法。如果所有数据都合法，那么该方法将返回True，
# 并将所有的表单数据转存到它的一个叫做cleaned_data的属性中，该属性是以个字典类型数据。# cleaned_data就是读取表单返回的值，返回类型为字典dict型，这里就是取的为数据库里面username
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = "该用户还未通过邮件确认！"
                    return render(request, 'login/login.html', locals())

                if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())
#这里默认得有这个方法吧，如果没有这个会报错。
    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())

def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
# message在login前端显示0，如果邮箱不合符格式不能提交renxiangqian@，并提示检查填写的内容。1，先检测验证码是否错误，并提示检查填写的内容。2，如果用户名存在提示已存在3，邮箱重复
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户，数据里面name=网页里面username

                new_user = models.User()
                new_user.name = username
                new_user.password = hash_code(password1)  # 使用加密密码
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_email(email, code)
                #调用send_email函数给邮箱发送邮件，然后必须去验证才能登陆。

                message = '请前往注册邮箱，进行邮件确认！'
                return render(request, 'login/confirm.html', locals())  # 跳转到等待邮件确认页面。
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    #flush()方法是比较安全的一种做法，而且一次性将session中的所有内容全部清空，确保不留后患。
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")
#当邮件链接被点击之后才会访问址http://127.0.0.1:8000（这个地址需要是一个外网地址，否则外网不能用）/confirm（进入url然后进入view）/?code={}"和code的具体数值，进入这个函数

def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'login/confirm.html', locals())
