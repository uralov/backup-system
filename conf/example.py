# -*- coding: utf-8 -*-
"""
You need create config file 'yandex.py' based on this file
"""
from os import path

email_config = {
    'host': 'smtp.yandex.ru',
    'port': 587,
    'user': 'noreply@vdole.net',
    'password': '',
    'from_email': 'Backup system <noreply@vdole.net>',
    'admin_email': 'example@gmail.com',
}

# your may add many projects in config
projects = [
    {
        'name': 'project_name',
        'bases': [
            {
                'host': 'localhost',
                'user': '',
                'password': '',
                'base_name': '',
            },
        ],
        'dirs': [
            '/var/directory2',
            '/var/directory',
        ],
        'dirs_scp': [
            'user@server:/directory/directory',
        ]
    },
]

backup_root_dir = path.join(
    path.dirname(path.dirname(path.realpath(__file__))),
    'result'
)
dst_root_dir = '~/Yandex.Disk/backup/'