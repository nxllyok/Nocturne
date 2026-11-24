from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session,
    abort
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from urllib.parse import urlsplit

from app import db
from app.models import User, Post
from app.forms import RegistrationForm, LoginForm, PostForm
from app.translations import translate

main = Blueprint("main", __name__)


def tr(key):
    return translate(session.get("language", "en"), key)


def safe_local_url(target):
    if not target:
        return False

    parts = urlsplit(target)

    return (
        not parts.scheme
        and not parts.netloc
        and target.startswith("/")
        and not target.startswith("//")
    )


@main.route("/")
def index():
    page = request.args.get("page", 1, type=int)

    pagination = Post.query.order_by(
        Post.created_at.desc()
    ).paginate(
        page=page,
        per_page=6,
        error_out=False
    )

    posts = pagination.items

    featured_post = None

    if page == 1 and posts:
        featured_post = posts[0]

    return render_template(
        "index.html",
        pagination=pagination,
        posts=posts,
        featured_post=featured_post
    )


@main.route("/post/<int:post_id>")
def post_detail(post_id):
    post = db.get_or_404(Post, post_id)

    return render_template(
        "post_detail.html",
        post=post
    )


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        username = form.username.data.strip()

        if User.query.filter_by(email=email).first():
            flash(tr("email_exists"), "error")
            return render_template("register.html", form=form)

        if User.query.filter_by(username=username).first():
            flash(tr("username_exists"), "error")
            return render_template("register.html", form=form)

        user = User(
            username=username,
            email=email
        )

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(tr("registration_success"), "success")

        return redirect(url_for("main.login"))

    return render_template(
        "register.html",
        form=form
    )


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            login_user(user)

            flash(tr("login_success"), "success")

            next_page = request.args.get("next")

            if safe_local_url(next_page):
                return redirect(next_page)

            return redirect(url_for("main.index"))

        flash(tr("invalid_login"), "error")

    return render_template(
        "login.html",
        form=form
    )


@main.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()

    flash(tr("logout_success"), "success")

    return redirect(url_for("main.index"))


@main.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            author=current_user
        )

        db.session.add(post)
        db.session.commit()

        flash(tr("post_created"), "success")

        return redirect(
            url_for("main.post_detail", post_id=post.id)
        )

    return render_template(
        "create_post.html",
        form=form
    )


@main.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)

    if post.user_id != current_user.id:
        abort(403)

    form = PostForm(obj=post)

    if form.validate_on_submit():
        post.title = form.title.data.strip()
        post.content = form.content.data.strip()

        db.session.commit()

        flash(tr("post_updated"), "success")

        return redirect(
            url_for("main.post_detail", post_id=post.id)
        )

    return render_template(
        "edit_post.html",
        form=form,
        post=post
    )


@main.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)

    if post.user_id != current_user.id:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash(tr("post_deleted"), "success")

    return redirect(url_for("main.index"))


@main.route("/language/<language>")
def change_language(language):
    if language not in ("en", "de", "ru"):
        language = "en"

    session["language"] = language

    target = request.referrer

    if safe_local_url(target):
        return redirect(target)

    return redirect(url_for("main.index"))


@main.app_errorhandler(403)
def forbidden(error):
    return render_template(
        "error.html",
        code=403,
        message=tr("not_allowed")
    ), 403


@main.app_errorhandler(404)
def not_found(error):
    return render_template(
        "error.html",
        code=404,
        message=tr("not_found")
    ), 404