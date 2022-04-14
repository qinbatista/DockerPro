#### RUN
> 22：ssh，18184：下载工具 80:网站
```
docker run -itv /root/repositories:/root/repositories qinbatista/gitrepositoriesupdate
```

> build

```
docker build -t qinbatista/gitrepositoriesupdate .
```

