#### RUN
> 22：ssh，18184：下载工具 80:网站
```
docker run -itv /root:/root -v /root/redeemsystem:/root/redeemsystem -p 10007:10007  qinbatista/redeemsystem
```

> build

```
docker build -t qinbatista/redeemsystem .
```

