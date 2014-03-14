# -*- coding: utf-8 -*-
from conf.yandex import projects, backup_root_dir, dst_root_dir, email_config
from processors import YandexProcessor

processor = YandexProcessor(**{
    'backup_root_dir': backup_root_dir,
    'dst_root_dir': dst_root_dir,
    'email_config': email_config,
})

# проходим по проектам
for project in projects:
    processor.process_project(project_data=project)
# заливаем файлы на яндекс диск
processor.copy_result_files_yandex()
# удаляем старые бэкапы на яндексе
processor.delete_old_backup_yandex(days=5)
# удаляем все директории бэкапов кроме последней
processor.delete_old_backup()