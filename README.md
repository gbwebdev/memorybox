# memorybox

![Memorybox logo](./memorybox.svg?raw=true "Memorybox logo")

Memorybox is a lightweight webapp that reveals a new memory picture everyday.

It can also print the picture on a peripage thermal printer.

## How it works

TODO

## The story behind

I wanted to make something special for my best friend's wedding.

The idea is that your wedding is one of the best days of your life... but it goes by really fast ! So I had this idea to give the grooms a small thermal printer that would print a reminder of this special day every day for... as long as there are pictures !

I asked all the guests to send me privately special pictures of the d-day with a captation.



# Remote access

Sur le serveur principal :
```
docker-compose -f /var/containers/maven-memorybox/docker-compose.yaml  exec ssh-tunnel /bin/sh
ssh -i /home/tunneluser/.ssh/id_ed25519 maven@127.0.0.1 -p 8022
```
Passphrase dans vaultwarden

