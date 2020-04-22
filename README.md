# weewx_to_ROMMA
Extension Weewx pour envoyer depuis weewx les données sur le réseau de ROMMA (http://www.romma.fr).

Les données ne seront accepées par le serveur de ROMMA que si l'identifiant de la station et son mot de passe sont correctement renseignés et valides.
Ces informations vous seront communiquées par ROMMA lors de l'enregistremenet de votre station.

##Installation de l'extension
Depuis le terminal :
  ```
  wget http://romma.fr/weewx/romma.zip
  wee_extension --install=romma.zip
  ```
Une fois l'extension installée, il faudra remplacer dans la section [StdRESTful] [[Romma]] de weewx.conf les champs id et password par les vôtres:
  ```
  [StdRESTful] 
   ...
   ...
  [[Romma]]
     id : 999,
     password: XXXXXX
     Server_url: .......
     ... 
   ```
 999 doit être remplacé par l'id de votre station et 
XXXXXX doit être remplacé par le mot de passe de votre station

**Pour que les changements soient effectifs, il faudra stopper et relancer weewx.**
