#### RUN
> 22：ssh，18184：下载工具 80:网站
```
docker run -itv /root/download:/root/download -v /root/Repositories:/Repositories -p 10022:22 qinbatista/debian_synology
```

```
docker build -t qinbatista/debian_synology .
```



**端口**

10022端口用于ssh远程连接

7000-8030端口用于ssr连接

**文件**

根目录又build_git_server.py用于git仓库的操作

**目录**

/root/download 用于远程下载服务器

**功能**

youtubedl下载视频

instagram-scraper下载照片

aria2下载下载链接