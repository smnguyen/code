##
# Social Web Comment Ranking
# CS224U Spring 2014
# Stanford University 
#
# Database interface, using SQLAlchemy
#
# Ian F. Tenney
# May 10, 2014
##

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker

Base = declarative_base()

#################################
# Miscellaneous type converters #
# and helper functions          #
#################################

# Conditional requests, in case Author is missing
def get_author_id(author):
    try: return a.fullname # full identifier: t2_id
    except: return None

def get_author_name(author):
    try: return a.name # human-readable username
    except: return None

# Timestamp converter
from datetime import datetime
def time_from_ms(t_ms):
    dt = datetime.utcfromtimestamp(t_ms)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


class Submission(Base):
    __tablename__ = 'submissions'
    
    # Metadata
    # id = Column(Integer, primary_key=True)
    sub_id = Column(String, primary_key=True)   # reddit submission ID
    user_id = Column(String)                # reddit author ID
    subreddit_id = Column(String)           # reddit subreddit ID
    timestamp = Column(DateTime)            # post time

    # Set up one->many relationship with comments
    comments = relation("Comment", backref="submission")

    # Core data
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    score = Column(Integer)
    
    # Additional post info
    stickied = Column(Boolean)      # sticky post
    distinguished = Column(String)  # ???
    gilded = Column(Integer)        # reddit gold

    # Domain and URL info
    domain = Column(String)
    short_link = Column(String)
    permalink = Column(String)

    def __init__(self, praw_obj=None, **kwargs):
        if not praw_obj: 
            return super(Submission, self).__init__(**kwargs)
        
        # If a PRAW submission object is given
        s = praw_obj
        
        self.sub_id = s.fullname    # full identifier: type_id
        self.user_id = get_author_id(s.author)  # author.fullname
        self.subreddit_id = s.subreddit_id      # subreddit identifier
        self.timestamp = datetime.utcfromtimestamp(s.created_utc)

        self.title = s.title
        self.text = s.selftext
        self.score = s.score

        self.stickied = s.stickied
        self.distinguished = s.distinguished
        self.gilded = s.gilded

        self.domain = s.domain
        self.short_link = s.short_link
        self.permalink = s.permalink

    def __repr__(self):
        return "Submission(%s,\"%s\"): \n%.140s" % (self.sub_id, 
                                                   self.title, 
                                                   self.text)
    
class Comment(Base):
    __tablename__ = 'comments'

    # Metadata
    # id = Column(Integer, primary_key=True)
    com_id = Column(String, primary_key=True)   # reddit comment ID
    user_id = Column(String)                # reddit author ID
    subreddit_id = Column(String)           # reddit subreddit ID
    parent_id = Column(String)              # reddit parent ID (submission, or other comment)
    timestamp = Column(DateTime)            # post time

    # Relationship: back to Submission object
    sub_id = Column(String, ForeignKey('submissions.sub_id'))

    # Core data
    text = Column(String, nullable=False)
    score = Column(Integer)
    
    # Additional post info
    distinguished = Column(String)  # ???
    gilded = Column(Integer)        # reddit gold
    is_root = Column(Boolean)       # top-level comment

    # URL info
    permalink = Column(String)

    def __init__(self, praw_obj=None, **kwargs):
        if not praw_obj: 
            return super(Submission, self).__init__(**kwargs)
    
        # If a PRAW submission object is given
        c = praw_obj
        
        self.com_id = c.fullname    # full identifier: type_id
        self.user_id = get_author_id(c.author)  # author.fullname
        self.subreddit_id = c.subreddit_id      # subreddit identifier
        self.parent_id = c.parent_id            # parent identifier
        self.timestamp = datetime.utcfromtimestamp(c.created_utc)

        self.text = c.body
        self.score = c.score

        self.distinguished = c.distinguished
        self.gilded = c.gilded
        self.is_root = c.is_root

        self.permalink = c.permalink

    def __repr__(self):
        return "Comment(%s): \n%.140s" % (self.com_id, 
                                          self.text)
