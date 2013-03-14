# -*- coding: utf-8 -*-
import datetime
import os
import re
import easywebdav

class Processor(object):

    def __init__(self, *args, **kwargs):
        self._date = str(datetime.date.today())
        self._root_local_directory = kwargs.get('root_local_directory')
        self._target_local_directory = os.path.join(self._root_local_directory, self._date)
        self._target_remote_directory = kwargs.get('target_remote_directory')
        self._webdav = kwargs.get('webdav')
        self._result_files = []

    def prepare_result_directory(self):
        if (not os.path.exists(self._root_local_directory)):
            os.mkdir(self._root_local_directory)
        os.chdir(self._root_local_directory)
        if (os.path.exists(self._target_local_directory)):
            self.delete_result_directory()
        os.mkdir(self._target_local_directory)
        os.chdir(self._target_local_directory)

    def process_project(self, project_data):
        project_name = project_data.get('name')
        project_result_dir = os.path.join(self._target_local_directory, project_name)
        project_result_dir_bases = os.path.join(project_result_dir, 'bases')
        project_result_dir_dirs = os.path.join(project_result_dir, 'dirs')

        # create dir for project
        os.mkdir(project_result_dir)
        # create dir for bases
        os.mkdir(project_result_dir_bases)
        # create dir for dirs
        os.mkdir(project_result_dir_dirs)

        # дампим базы
        os.chdir(project_result_dir_bases)
        bases = project_data.get('bases')
        for base in bases:
            os.system('mysqldump --host=%s -u%s -p%s %s > %s__%s.sql' % (base.get('host'),
                                                                   base.get('user'),
                                                                   base.get('password'),
                                                                   base.get('base_name'),
                                                                   base.get('base_name'),
                                                                   self._date))

        # копируем директории
        os.chdir(project_result_dir_dirs)
        for dir in project_data.get('dirs'):
            os.system('cp -R %s %s' % (dir,
                                       os.path.join(project_result_dir_dirs, os.path.basename(dir))))
        # копируем директории по scp
        for dir in project_data.get('dirs_scp'):
            os.system('scp -rpq %s %s' % (dir,
                                       os.path.join(project_result_dir_dirs, os.path.basename(dir))))

        # а теперь пакуем в архив
        os.chdir(project_result_dir)
        filename = "%s__%s.tar.gz" % (project_name, self._date)
        os.system('tar -czf %(file_name)s bases dirs' % {'file_name': filename})
        # добавляем архив в результирующие файлы
        self._result_files.append(os.path.join(project_result_dir, filename))

    def upload_files_webdav(self, webdav_config):
        """
        Заливаем файлы
        :param dict files_list: массив путей к локальным файлам
        """
        # создадим необходимую папку
        target_remote_directory = self._target_remote_directory + self._date + '/'
        try:
            self._webdav.mkdir(target_remote_directory)
        except easywebdav.OperationFailed:
            pass

        # а теперь заливаем туда файлы
        for obj in self._result_files:
            os.system('curl --user %s:\'%s\' -T "{%s}" https://webdav.yandex.ru%s' % (
                webdav_config.get('username'),
                webdav_config.get('password'),
                obj,
                target_remote_directory,
            ))
            # self._webdav.upload(obj, target_remote_directory + obj.split('/')[-1])

    def clear_old_backups_webdav(self, days=10):
        """
        Удаляем директории старше заданного количества дней
        :param int days: дни в течении которых бэкап считается актуальным
        """
        # крайняя дата, <= которой необходимо удалить директории с бэкапами
        limit_top_date = str(datetime.date.today() - datetime.timedelta(days=days))
        pattern = r'^%s(\d{4}-\d{2}-\d{2})/$' % self._target_remote_directory

        for obj in self._webdav.ls(self._target_remote_directory):
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

    def delete_result_directory(self):
        os.system('rm -r %s' % self._target_local_directory)

    def delete_old_directory(self, count_live_day=1):
        os.chdir(self._root_local_directory)
        limit_top_date = str(datetime.date.today() - datetime.timedelta(days=count_live_day))
        for dir_name in os.listdir(self._root_local_directory):
            if dir_name <= limit_top_date:
                os.system('rm -r %s' % dir_name)



