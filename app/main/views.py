# "Standard libs" imports
import os                              # FIXME no longer needed i think
import json                            # same
from glob import glob                  # same
from config import config, LIQUIDSOAP_TOKEN # same
from uuid import uuid4                 # same
from datetime import date

# Flask stuff
from flask import (Flask, render_template, request,
                   url_for, jsonify, redirect, flash) # same
from sqlalchemy import cast, Date

# Specific app stuff
from . import main
from .forms import SubscribeForm       # same
from .partial_content import *
# from .jinja_custom_filters import *
from .. import db                      # same
from app.models.admin import *
from app.models.event import Event
from app.models.podcast import Podcast
from app.models.section import Section
from app.models.contributor import Contributor
from app.models.blog import BlogPost
from app.models.event import Event
from app.models.channel import Channel
from app.models.tag import Tag
from app.models.page import Page

app = Flask(__name__)


#########################
#  Main pages           #
#########################

partial_content = partial_content_decorator()
partial_content_no_history = partial_content_no_history_decorator()

@main.route('/')
@partial_content
def index():
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "index.haml",
                podcasts=Podcast.list(number=5),
                blog_posts = BlogPost.list(number=3),
                events = Event.query\
                .filter(cast(Event.begin, Date) >= date.today())\
                .order_by(Event.begin.asc())\
                  .limit(5).all()
            )
        }
    }


#########################
#  Pages                #
#########################

@main.route('/about')
@partial_content
def about():
    page = Page.query.get_or_404(1)
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "main_pages/about.haml",
                page=page
            ),
            'title': "À propos"
        }
    }

@main.route('/contrib')
@partial_content
def contribute():
    page = Page.query.get_or_404(2)
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "main_pages/contribute.haml",
                page=page
            ),
            'title': "Contribuer"
        }
    }

#########################
#  Podcasts             #
#########################

@main.route('/podcasts')
@partial_content
def podcasts():
    page = request.args.get('page', 1, type=int)
    pagination = Podcast.query                         \
        .order_by(Podcast.timestamp.desc())            \
        .paginate(page, per_page=10, error_out=False)
    podcasts = pagination.items
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "main_pages/podcasts.haml",
                podcasts=podcasts,
                pagination=pagination
            ),
            'title': "Podcasts"
        }
    }

@main.route('/podcasts/<id>')
@partial_content
def podcast(id):
    podcast = Podcast.query.get_or_404(id)
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "elem_pages/podcast.haml",
                elem=podcast
            ),
            'title': podcast.name,
            'description': podcast.description
        }
    }

@main.route('/podcasts/<id>/play')
@partial_content_no_history
def play(id):
    podcast = Podcast.query.get_or_404(id)
    return {
        'function': 'player.load.bind(player)',
        'content': {
            "link" : podcast.link,
            "title" : podcast.name,
            "channel": podcast.channel_id
        }
    }

##############################
#  Contributors/Collectives  #
##############################

@main.route('/contributors')
@main.route('/collectives')
@partial_content
def contributors():
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "main_pages/contributors.haml",
                contributors=Contributor.list(),
                collectives=Collective.list()
            ),
            'title': "Contributeurs",
            'description': "Liste des contributeurs de Radio Rhino."
        }
    }

@main.route('/contributors/<id>')
@partial_content
def contributor(id):
    contributor = Contributor.query.get_or_404(id)
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "elem_pages/contributor.haml",
                elem=contributor
            ),
            'title': contributor.name,
            'description': contributor.description
        }
    }

@main.route('/collectives/<id>')
@partial_content
def collective(id):
    collective = Collective.query.get_or_404(id)
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "elem_pages/contributor.haml",
                elem=collective
            ),
            'title': collective.name,
            'description': collective.description
        }
    }

#########################
#  Channels             #
#########################

@main.route('/channels')
@partial_content
def channels():
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "main_pages/channels.haml",
                channels=Channel.list()
            ),
            'title': "Chaînes",
            'description': "Les Chaînes de Radio Rhino"
        }
    }


@main.route('/channels/<id>')
@partial_content
def channel(id):
    channel = Channel.query.get_or_404(id)
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "elem_pages/contributor.haml",
                elem=channel
            ),
            'title': channel.name
        }
    }

#########################
#  Blogs                #
#########################

@main.route('/blogs')
@partial_content
def blogs():
    page = request.args.get('page', 1, type=int)
    pagination = BlogPost.query                         \
        .order_by(BlogPost.timestamp.desc())            \
        .paginate(page, per_page=10, error_out=False)
    blog_posts = pagination.items
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "main_pages/blogs.haml",
                blog_posts=BlogPost.list(number=10),
                pagination = pagination
            ),
            'title': "Blogs",
            'description': "Les articles de blog de Radio Rhino"
        }
    }

@main.route('/blogs/<id>')
@partial_content
def blog(id):
    blog_post = BlogPost.query.get_or_404(id)
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "elem_pages/blog.haml",
                elem=blog_post
            ),
            'title': blog_post.name
        }
    }


#########################
#  Agendas              #
#########################

@main.route('/agendas')
@partial_content
def agendas():
    page = request.args.get('page', 1, type=int)
    pagination = Event.query                         \
        .order_by(Event.begin.asc())            \
        .paginate(page, per_page=10, error_out=False)
    events = pagination.items
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "main_pages/agendas.haml",
                events = events,
                pagination = pagination),
            'title': "Agendas"
        }
    }

@main.route('/agendas/<id>')
@partial_content
def agenda(id):
    event = Event.query.get_or_404(id)
    return {
        'function': 'displayMain',
        'content': {
            'template': render_template(
                "elem_pages/agenda.haml",
                elem=event
            ),
            'title': event.name
        }
    }

#########################
#  Static stuff         #
#########################

@main.route('/get_live')
@partial_content_no_history
def get_live():

    live, next_live_in = Event.closest_live()

    stream_url_play = url_for('main.podcast', id=live.podcast().id)

    return {
        'function': 'updateLive',
        'content': {
            "next_live_in" : next_live_in,
            "stream_url_play" : stream_url
        }
    }
