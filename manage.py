import os
from app import create_app, db
from app.models import User, Role, Permission
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

app = create_app(os.getenv('FLASKY_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    # discover(start_dir='tests', pattern='test*.py')  自动查找，返回一个 test suite实例
    unittest.TextTestRunner(verbosity=2).run(tests)  # 执行测试用例

if __name__ == '__main__':
    manager.run()
