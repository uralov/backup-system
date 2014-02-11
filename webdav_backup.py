# -*- coding: utf-8 -*-
import easywebdav
from conf.webdav import projects, backup_root_dir, webdav_config, email_config
from processors import WebdavProcessor


processor = WebdavProcessor(**{
    'backup_root_dir': backup_root_dir,
    'dst_root_dir': '/backup/',
    'webdav': easywebdav.connect(**webdav_config),
    'email_config': email_config,
})


# проходим по проектам
for project in projects:
    processor.process_project(project_data=project)
# заливаем файлы на яндекс диск
processor.copy_result_files_webdav(webdav_config=webdav_config)
# удаляем старые файлы
processor.delete_old_backup_webdav()
# удаляем все директории бэкапов кроме последней
processor.delete_old_backup()