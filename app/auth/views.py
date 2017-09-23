from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from ..models import User
from .. import db
from ..email import send_email


# ##################### 注册——登录——登出 ########################
@auth.route('/login', methods=['get', 'post'])
def login():  # 登录页面
    form = LoginForm()  # 获取表单
    if form.validate_on_submit():  # 如果不是有效的提交，则还是login.html
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):  # 查询是否存在该邮箱并且密码是否正确
            login_user(user, remember=form.remember_me.data)  # 登录该用户
            return redirect(request.args.get('next') or url_for('main.index'))  # 返回到首页
        flash(message='Invalid username or password')  # 提交错误的信息后，会弹出这个信息
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():  # 登出，前提条件是login required
    logout_user()
    flash(message='You have been logged out')
    return redirect(url_for('main.index'))  # 登出之后返回到首页


@auth.route('/register', methods=['get', 'post'])
def register():  # 注册页面
    form = RegistrationForm()  # 获取注册表单
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)  # 添加用户信息
        db.session.add(user)
        db.session.commit()  # 将用户数据写入到数据库中
        token = user.generate_confirmation_token()  # 生成一个用来确认的token, 发送邮件来确认
        send_email(to=user.email, subject='confirm you account', template='auth/email/confirm',
                   user=user, token=token)
        flash(message='a confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


# ##################### 确认邮箱 ########################
@auth.route('/confirm/<token>')  # 这个是确认邮件中的url
@login_required
def confirm(token):
    if current_user.confirmed:  # 如果是已经确认的，则返回到首页，避免无意义的确认
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed you account. Thanks!')  # 并且将User.confirm设为True
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():  # 重新发送一封确认邮件
    token = current_user.generate_confirmation_token()
    send_email(to=current_user.email,
               subject='confirm you account',
               template='auth/email/confirm',
               user=current_user, token=token)
    flash('a new confirmation email has been sent to you email')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:  # 普通用户——is_anonymous=False
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


# ##################### 修改密码 ########################
@auth.route('/change-password', methods=['get', 'post'])
@login_required
def change_password():  # 在login的前提出修改密码
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):  # 首先确认输入了正确的旧密码
            current_user.password = form.password.data  # 设置新的密码
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template('auth/change_password.html', form=form)


# ##################### 重设密码 ########################
# 先有password_reset_request，然后再有password_reset
@auth.route('/reset', methods=['get', 'post'])
def password_reset_request():  # 生成修改密码的一个url，并以邮件的形式发送
    if not current_user.is_anonymous:  # 如果已经登录了，就直接重定向到index
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_confirmation_token()
            send_email(to=user.email, subject='reset your password',
                       template='auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('an email with instructions to reset your password has been sent to you')
    return render_template('auth/reset_password.html', form=form)


# 先有password_reset_request，然后再有change_password
@auth.route('/reset/<token>', methods=['get', 'post'])
def password_reset(token):  # 确认邮件中的url, 打开之后会获取PasswordResetForm表单
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


# ##################### 修改邮箱 ########################
@auth.route('/change-email', methods=['get', 'post'])  # 提出修改邮箱的url
@login_required
def change_email_request():  # 生成修改邮箱的一个url
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token()
            send_email(to=new_email, subject='Confirm your email address',
                       template='auth/email/change_email',
                       user=current_user, token=token)
            flash(message='an email with instructions to confirm your new email address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('invalid email or password.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')  # 确认邮件中的url
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('invalid request.')
    return redirect(url_for('main.index'))