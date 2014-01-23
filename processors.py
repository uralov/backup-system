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
        self._src_root_dir = kwargs.get('src_root_dir')
        self._dst_root_dir = kwargs.get('dst_root_dir')
        self._src_dir = os.path.join(
            self._src_root_dir,
            self._date
        )
        self._email_config = kwargs.get('email_config')

    @staticmethod
    def delete_directory(path):
        os.system('rm -r %s' % path)

    def get_backup_filename(self, project_name):
        filename = "%s__%s.tar.gz" % (project_name, self._date)
        return filename

    def prepare_backup_directory(self):
        if not os.path.exists(self._src_root_dir):
            os.mkdir(self._src_root_dir)
        os.chdir(self._src_root_dir)
        if os.path.exists(self._src_dir):
            self.delete_directory(self._src_dir)
        os.mkdir(self._src_dir)
        os.chdir(self._src_dir)

    def delete_old_backup_directory(self, count_live_day=1):
        os.chdir(self._src_root_dir)
        limit_top_date = str(datetime.date.today() - datetime.timedelta(days=count_live_day))
        for dir_name in os.listdir(self._src_root_dir):
            if dir_name <= limit_top_date:
                os.system('rm -r %s' % dir_name)

    def send_mail(self, msg='', sbj='Backup problem'):
        mail_conf = self._email_config

        msg = MIMEText(msg)
        msg['Subject'] = sbj
        msg['From'] = mail_conf['from_email']
        msg['To'] = mail_conf['admin_email']

        smtp = smtplib.SMTP(host=mail_conf['host'], port=mail_conf['port'])
        smtp.login(user=mail_conf['user'], password=mail_conf['password'])
        smtp.sendmail(from_addr=mail_conf['from_email'], to_addrs=mail_conf['admin_email'],
                      msg=msg.as_string())
        smtp.quit()


class WebdavProcessor(BaseProcessor):
    def __init__(self, *args, **kwargs):
        super(WebdavProcessor, self).__init__(*args, **kwargs)
        self._webdav = kwargs.get('webdav')
        self._result_files = []

    def process_project(self, project_data):
        """
        Подготавливаем бэкап
        """
        project_name = project_data.get('name')
        result_dir = os.path.join(self._src_dir, project_name)
        result_dir_bases = os.path.join(result_dir, 'bases')
        result_dir_dirs = os.path.join(result_dir, 'dirs')

        # create directory for project
        os.mkdir(result_dir)
        # create directory for bases
        os.mkdir(result_dir_bases)
        # create directory for dirs
        os.mkdir(result_dir_dirs)

        # дампим базы
        os.chdir(result_dir_bases)
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

        # копируем директории
        os.chdir(result_dir_dirs)
        for directory in project_data.get('dirs'):
            os.system('cp -R %s %s' % (
                directory,
                os.path.join(result_dir_dirs, os.path.basename(directory))
            ))
        # копируем директории по scp
        for directory in project_data.get('dirs_scp'):
            os.system('scp -rpq %s %s' % (
                directory,
                os.path.join(result_dir_dirs, os.path.basename(directory))
            ))

        # а теперь пакуем в архив
        os.chdir(result_dir)
        filename = self.get_backup_filename(project_name)
        os.system('tar -czf %(file_name)s bases dirs' % {'file_name': filename})
        # добавляем архив в результирующие файлы
        self._result_files.append(os.path.join(result_dir, filename))

    def upload_files_webdav(self, webdav_config):
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

    def clear_old_backups_webdav(self, days=10):
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
                    # здесь возникает какое-то исключение - но по факту удаление происходит
                    pass


class LocalCopyProcessor(BaseProcessor):
    """
    Создание локальных копий бэкапа, для большей надёжности
    """
    def backup_exist(self, project_data, file_path):
        # проверка существования файла бэкапа проекта
        project_name = project_data.get('name')
        file_name = self.get_backup_filename(project_name)
        full_file_path = os.path.join(file_path, file_name)
        return os.path.exists(full_file_path)

    def backup_copy(self, src, dst):
        os.system('cp -R %s %s' % (src, dst))





