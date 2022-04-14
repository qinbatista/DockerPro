#### RUN
> 22：ssh，18184：下载工具 80:网站

后台运行
```
docker run -itdv /Video:/Video -v /OneDrive:/OneDrive -p 10015:10015  qinbatista/folder_sync
```

窗口运行
```
docker build -t qinbatista/folder_sync .
```

docker run -itv /Video:/Video -v /OneDrive:/OneDrive -p 10015:10015  qinbatista/folder_sync