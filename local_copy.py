# -*- coding: utf-8 -*-
from conf.config_local import projects, backup_root_dir, email_config
from processors import LocalCopyProcessor


processor = LocalCopyProcessor(**{
    'src_root_dir': backup_root_dir,
    'dst_root_dir': '/backup/',
    'email_config': email_config,
})

# for project in projects:
#     if not processor.backup_file_exist(project):
#         processor.send_mail(msg='Backup %s does not exist' %
#                                 processor.get_backup_filename(project['name']))
#     processor.backup_file_copy(project)