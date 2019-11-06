


```
docker run -d -p 80:5000 afterpay:latest
630bb47d72e18891502f82250f23d040d5041d1dead31a215580d4386d15c4cf
```

```
james@ip-10-101-32-173~/P/application-afterpay> docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                  NAMES
630bb47d72e1        afterpay:latest     "flask run --host 0.…"   12 minutes ago      Up 12 minutes       0.0.0.0:80->5000/tcp   awesome_meninsky

```