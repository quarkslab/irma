from lib.irma.database.sqlhandler import SQLDatabase
from lib.irma.database.sqlobjects import Base, Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Scan(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True))
    scanid = Column(String)
    status = Column(Integer)
    nbfiles = Column(Integer)
    taskid = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return "Scan {0}:\t{1} file(s)\t status: '{2}'\ttaskid: '{3}'\tuser_id: {4}\n".format(self.scanid, self.nbfiles, self.label[self.status], self.taskid, self.user_id)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    rmqvhost = Column(String)
    ftpuser = Column(String)
    quota = Column(Integer)
    scan = relationship("Scan")

    def __repr__(self):
        return "User {0}:\trmq_vhost: '{1}'\t ftpuser: '{2}'\tquota: '{3}'\n".format(self.name, self.rmqvhost, self.ftpuser, self.quota)


if __name__ == "__main__":
    # create all dbs
    import config

    sql = SQLDatabase(config.brain_config['sql_brain'].engine + config.brain_config['sql_brain'].dbname)
    Base.metadata.create_all(sql._db)
    user = User(name="test1", rmqvhost="mqfrontend", ftpuser="frontend1", quota=10000)
    sql.add(user)
    sql.commit()

