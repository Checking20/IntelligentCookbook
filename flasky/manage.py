import os
from app import create_app, db
from flask_script import Manager, Shell, Command
from app.main.recommend.itemCF import ItemBasedCF as ICF
from app.main.recommend.userCF import UserBasedCF as UCF
from app.main.recommend.data.predata import Predata

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db)


# 自定义命令:Calculate——计算用于推荐的表
class Calculate(Command):
    # 命令内容
    def run(self):
        # 读取数据
        pd = Predata()
        icf = ICF()
        ucf = UCF()
        icf.get_dataset(pd)
        ucf.get_dataset(pd)
        # 计算
        icf.calc_cookbook_sim()
        ucf.calc_user_sim()
        # 写入数据库
        icf.save()
        ucf.save()

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('calculate', Calculate())
manager.add_command('db')

if __name__ == '__main__':
    manager.run()
