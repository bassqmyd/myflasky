import os

basedir = os.path.abspath(os.path.dirname(__file__))
# print(basedir)  # D:\Zesktop_Important_File\nowcoder\flasky


class Config(object):
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = '945581235@qq.com'
    MAIL_PASSWORD = 'kuzxwuwiijtabcba'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = '945581235@qq.com'
    FLASKY_ADMIN = '945581235@qq.com'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data_dev.sqlite')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data_test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {'development': DevelopmentConfig,
          'testing': TestConfig,
          'production': ProductionConfig,
          'default': DevelopmentConfig}
