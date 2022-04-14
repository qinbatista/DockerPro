#### RUN
> 22：ssh，18184：下载工具 80:网站
```
docker run -itv /root/download:/root/download_folder  -p 10008:10008 -p 21:21 -p 2024:2024 -p 1023:1023 -p 1024:1024 qinbatista/httpsharing
```

> build

```
docker build -t qinbatista/httpsharing .
```

