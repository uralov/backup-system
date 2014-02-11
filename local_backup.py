# -*- coding: utf-8 -*-
from conf.local import projects, backup_root_dir, email_config
from processors import LocalCopyProcessor


processor = LocalCopyProcessor(**{
    'backup_root_dir': backup_root_dir,
    'email_config': email_config,
})

for project in projects:
    if not processor.backup_exist(project_data=project):
        processor.send_mail(msg='Backup %s does not exist' %
                                processor.get_backup_path(project))
    processor.process_project(project_data=project)

processor.delete_old_backup(count_live_day=30)