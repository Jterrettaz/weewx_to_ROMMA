# weewx_to_ROMMA
Extension Weewx pour envoyer depuis weewx les données sur le réseau de ROMMA (http://www.romma.fr).

Les données ne seront accepées par le serveur de ROMMA que si l'identifiant de la station et son mot de passe sont correctement renseignés et valides.
Ces informations vous seront communiquées par ROMMA lors de l'enregistrement de votre station.


## Installation de l'extension
Il faut tout d'abord configurer weewx pour que les températures minimales et maximales de chaque enregistrement soient sauvegardés dans la base de donnée de weewx :
 1. Ajouter à la fin du fichier **extensions.py** (situé dans le dossier "utilisateur" de weewx (le plus souvent /usr/share/weewx/user ou /home/weewx/bin/user)les lignes suivantes :
 ```python
   import weewx.units
   weewx.units.obs_group_dict['lowOutTemp'] = 'group_temperature'
   weewx.units.obs_group_dict['highOutTemp'] = 'group_temperature'
 ```
 
 2. Stopper Weewx et mettre à jour la base de donnée avec les nouveaux champs (**Weewx v4.5.0 ou plus récent**). 
 Dans une fenêtre terminal:
       ```python
       sudo wee_database --add-column=lowOutTemp
       sudo wee_database --add-column=highOutTemp
       ```
    En cas d'erreur (commande introuvable) et si weewx a été installé avec setup.py : 
       ```python
       sudo /home/weewx/bin/wee_database --add-column=lowOutTemp
       sudo /home/weewx/bin/wee_database --add-column=highOutTemp
       ```
    
    ou si weewx a été installé depuis un package DEB ou RPM:
       ```python
       sudo /usr/bin/wee_database --add-column=lowOutTemp
       sudo /usr/bin/wee_database --add-column=highOutTemp
       ```
 
  
  Les 2 nouveaux champs, **lowOutTemp** and **highOutTemp** sont maintenant ajoutés chaque fois qu'un enregistrement d'archive est ajouté dans la base de données d'archive de Weewx.

  3. Ensuite, depuis le terminal, installer l'extension:
  ```
  wget https://github.com/Jterrettaz/weewx_to_ROMMA/archive/refs/tags/romma.zip
  ```
  puis
  ```
  sudo wee_extension --install=romma.zip
  ```
  En cas d'erreur (commande introuvable) et si weewx a été installé avec setup.py :
  ```
  sudo /home/weewx/bin/wee_extension --install=romma.zip
  ```
  ou si weewx a été installé depuis un package DEB ou RPM:
  ```
  sudo /usr/bin/wee_extension --install=romma.zip
  ```
  4.Une fois l'extension installée, il faudra remplacer dans la section [StdRESTful] [[Romma]] de weewx.conf les champs id et password par les vôtres, et vérifier l'url du serveur  :
  ```
  [StdRESTful] 
   ...
   ...
  [[Romma]]
     id = 999
     password = XXXXXX
     server_url = https://www.romma.fr/donneesdeweewx.php
     ... 
   ```
 999 doit être remplacé par l'id de votre station et 
 
 
XXXXXX doit être remplacé par le mot de passe de votre station

**Pour que les changements soient effectifs, il faudra stopper et relancer weewx.**
