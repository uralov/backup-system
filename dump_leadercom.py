# -*- coding: utf-8 -*-
from config import projects, result_dir, webdav_config
from processor import Processor
import easywebdav

processor = Processor(**{
    'target_local_directory': result_dir,
    'target_remote_directory': '/backup/',
    'webdav': easywebdav.connect(**webdav_config),
})

# подготавливаем директорию для результата
processor.prepare_result_directory()
# проходим по проектам
for project in projects:
    processor.process_project(project_data=project)
# заливаем файлы
processor.upload_files()
# удаляем старые файлы
processor.clear_old_backups()
# удаляем директорию с результатом
processor.delete_result_directory()
