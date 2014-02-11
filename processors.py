# -*- coding: utf-8 -*-
import datetime
import os
import re
import easywebdav
import smtplib
from email.mime.text import MIMEText


class BaseProcessor(object):
    def __init__(self, *args, **kwargs):
        self._date = str(datetime.date.today())
        self._backup_root_dir = kwargs.get('backup_root_dir')
        self._backup_dir = os.path.join(self._backup_root_dir, self._date)
        self._email_config = kwargs.get('email_config')

        # подготоавливаем директорию для бэкапа
        self._prepare_backup_directory()

    @staticmethod
    def _create_directory(name):
        if not os.path.exists(name):
            os.mkdir(name)

    @staticmethod
    def _delete_directory(path):
        os.system('rm -r %s' % path)

    def _prepare_backup_directory(self):
        self._create_directory(self._backup_root_dir)
        os.chdir(self._backup_root_dir)
        if os.path.exists(self._backup_dir):
            self._delete_directory(self._backup_dir)
        self._create_directory(self._backup_dir)
        os.chdir(self._backup_dir)

    def _get_backup_filename(self, project_name):
        return "%s__%s.tar.gz" % (project_name, self._date)

    def _dump_dir(self, project_data, result_dir):
        self._create_directory(result_dir)
        os.chdir(result_dir)
        for directory in project_data.get('dirs'):
            os.system('cp -R %s %s' % (
                directory,
                os.path.join(result_dir, os.path.basename(directory))
            ))

    def _dump_dir_scp(self, project_data, result_dir):
        self._create_directory(result_dir)
        os.chdir(result_dir)
        for directory in project_data.get('dirs_scp'):
            os.system('scp -rpq %s %s' % (
                directory,
                os.path.join(result_dir, os.path.basename(directory))
            ))

    def _dump_mysql(self, project_data, result_dir):
        self._create_directory(result_dir)
        os.chdir(result_dir)

        bases = project_data.get('bases')
        for base in bases:
            os.system('mysqldump --host=%s -u%s -p%s %s > %s__%s.sql' % (
                base.get('host'),
                base.get('user'),
                base.get('password'),
                base.get('base_name'),
                base.get('base_name'),
                self._date)
            )

    def _archive_directory(self, directory, project_name):
        os.chdir(directory)
        file_name = self._get_backup_filename(project_name)
        os.system('tar -czf %(file_name)s bases dirs' % {'file_name': file_name})
        # добавляем архив в результирующие файлы
        return os.path.join(directory, file_name)

    def delete_old_backup(self, count_live_day=1):
        os.chdir(self._backup_root_dir)
        limit_top_date = str(datetime.date.today()
                             - datetime.timedelta(days=count_live_day))
        for dir_name in os.listdir(self._backup_root_dir):
            if dir_name <= limit_top_date:
                self._delete_directory(dir_name)

    def send_mail(self, msg='', sbj='Backup problem'):
        mail_conf = self._email_config

        msg = MIMEText(msg)
        msg['Subject'] = sbj
        msg['From'] = mail_conf['from_email']
        msg['To'] = mail_conf['admin_email']

        smtp = smtplib.SMTP(host=mail_conf['host'], port=mail_conf['port'])
        smtp.login(user=mail_conf['user'], password=mail_conf['password'])
        smtp.sendmail(
            from_addr=mail_conf['from_email'],
            to_addrs=mail_conf['admin_email'],
            msg=msg.as_string()
        )
        smtp.quit()


class WebdavProcessor(BaseProcessor):
    def __init__(self, *args, **kwargs):
        super(WebdavProcessor, self).__init__(*args, **kwargs)
        self._dst_root_dir = kwargs.get('dst_root_dir')
        self._webdav = kwargs.get('webdav')
        self._result_files = []

    def process_project(self, project_data):
        """
        Подготавливаем бэкап
        """
        project_name = project_data.get('name')
        result_dir = os.path.join(self._backup_dir, project_name)
        self._create_directory(result_dir)

        result_dir_bases = os.path.join(result_dir, 'bases')
        self._dump_mysql(project_data, result_dir_bases)

        result_dir_dirs = os.path.join(result_dir, 'dirs')
        self._dump_dir(project_data, result_dir_dirs)
        self._dump_dir_scp(project_data, result_dir_dirs)

        backup_file = self._archive_directory(result_dir, project_name)
        self._result_files.append(backup_file)

    def copy_result_files_webdav(self, webdav_config):
        """
        Заливаем файлы
        """
        # создадим необходимую папку
        destination_dir = self._dst_root_dir + self._date + '/'
        try:
            self._webdav.mkdir(destination_dir)
        except easywebdav.OperationFailed:
            pass

        # а теперь заливаем туда файлы
        for obj in self._result_files:
            os.system('curl --user %s:\'%s\' -T "{%s}" https://webdav.yandex.ru%s' % (
                webdav_config.get('username'),
                webdav_config.get('password'),
                obj,
                destination_dir,
            ))

    def delete_old_backup_webdav(self, days=10):
        """
        Удаляем директории старше заданного количества дней
        :param int days: дни в течении которых бэкап считается актуальным
        """
        # крайняя дата, <= которой необходимо удалить директории с бэкапами
        limit_top_date = str(datetime.date.today() - datetime.timedelta(days=days))
        pattern = r'^%s(\d{4}-\d{2}-\d{2})/$' % self._dst_root_dir

        for obj in self._webdav.ls(self._dst_root_dir):
            result = re.findall(pattern, obj.name)
            if len(result) != 1:
                continue
            name = result[0]
            if name <= limit_top_date:
                try:
                    self._webdav.rmdir(obj.name)
                except easywebdav.OperationFailed:
                    # возникает исключение, но по факту удаление происходит
                    pass


class LocalCopyProcessor(BaseProcessor):
    """
    Создание локальных копий бэкапа
    """

    def get_backup_path(self, project_data):
        project_name = project_data.get('name')
        file_path = project_data.get('dirs')[0]
        file_name = self._get_backup_filename(project_name)
        full_file_path = os.path.join(file_path, self._date, file_name)
        return full_file_path

    def backup_exist(self, project_data):
        # проверка существования файла бэкапа проекта
        backup_path = self.get_backup_path(project_data)
        return os.path.exists(backup_path)

    def process_project(self, project_data):
        backup_path = self.get_backup_path(project_data)
        os.system('cp %s %s' % (backup_path, self._backup_dir))







