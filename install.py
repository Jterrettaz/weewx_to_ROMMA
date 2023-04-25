# installer for ROMMA extension
# Distributed under terms of the GPLv3

from setup import ExtensionInstaller


def loader():
    return RommaInstaller()


class RommaInstaller(ExtensionInstaller):
    def __init__(self):
        super(RommaInstaller, self).__init__(
            version="2.0",
            name='romma',
            description='Envoi vers romma.fr.',
            author="Jacques Terrettaz",
            author_email="webmaster@meteo-sciez.fr",
            restful_services='user.romma.Romma',
            config={
                'StdRESTful': {
                    'Romma': {
                        'id': '999',
                        'password': 'XXXXXX',
                        'server_url': 'https://www.romma.fr/donneesdeweewx.php'}
                }
            },
            files=[('bin/user', ['bin/user/romma.py'])]
            )
