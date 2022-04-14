###Start command

```dockerfile
docker run -it -p 12345:12345/udp -p 12345:12345/tcp -p 53:53/udp -p 53:53/tcp --interface=docker0 --except-interface=lo --bind-interfaces qinbatista/ddns_server
```

