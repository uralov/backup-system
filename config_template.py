# -*- coding: utf-8 -*-
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
            '/var/www/project_name/1/',
            '/var/www/project_name/2/',
        ]
    },
]

result_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'result')
