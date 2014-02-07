# -*- coding: utf-8 -*-
from os import path

email_config = {
    'host': 'smtp.yandex.ru',
    'port': 587,
    'user': 'noreply@vdole.net',
    'password': 'OmBO0nJR0l9JeuY',
    'from_email': 'Backup system <noreply@vdole.net>',
    'admin_email': 'yralov87@gmail.com',
}

# your may add many projects in config
projects = [
    {
        'name': 'socnet_local_backup',
        'bases': [],
        'dirs': [
            '/home/listener/Yandex.Disk/Документы',
        ],
        'dirs_scp': []
    },
]

backup_root_dir = path.join(path.dirname(path.dirname(path.realpath(__file__))), 'result')