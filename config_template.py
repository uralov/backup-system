# -*- coding: utf-8 -*-
"""
You need create config file 'config.py' based on this file
"""
import os
webdav_config = {
    'host': 'webdav.yandex.ru',
    'protocol': 'https',
    'username': '',
    'password': '',
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

result_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'result')
