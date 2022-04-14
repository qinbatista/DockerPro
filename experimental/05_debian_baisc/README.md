#### RUN
> 22：ssh，18184：下载工具 80:网站
```
docker run -p 5900:5900 -e VNC_SERVER_PASSWORD=password --user apps --privileged qinbatista/chrome
```

> build

```
docker build -t qinbatista/chrome .
```

