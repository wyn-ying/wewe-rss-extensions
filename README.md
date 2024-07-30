# WeWe RSS 扩展管理组件

<h3 align="center">本项目用于扩展<a href="https://github.com/cooderl/wewe-rss">WeWe RSS</a>的部分功能

## 原理

extensions主程序启动时，会读取容器 `/app/data/conf` 目录下各组件的yaml配置文件

因此需要在容器启动前，先完成组件配置，用到组件的yaml放在`$(pwd)/data/conf/`目录下

之后通过`-v $(pwd)/data:/app/data`，确保容器的`/app/data/conf`目录挂载到宿主机的`$(pwd)/data/conf/`目录

## 功能

- [x] 定时通知机器人，支持飞书，钉钉，自定义...
- [ ] 内容过滤&通知
- [ ] 个性化更新配置
  ...

### 定时通知机器人

示例配置文件[notify_example.yaml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/notify_example.yaml)

- 支持多个同类型/不同类型的定时通知机器人，示例中为两个飞书机器人和一个钉钉机器人

- 支持为每个机器人设置独立的通知周期，分钟粒度

## 部署

### Docker Compose

- Mysql版参考 [docker-compose.yml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docker-compose.yml)
- Sqlite版参考 [docker-compose.sqlite.yml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docker-compose.sqlite.yml)

### Docker

#### Sqlite版

1. 参考 [扩展组件配置](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docs/configuation.md) 完成相关组件的配置，yaml配置文件放在目录 `$(pwd)/data/conf/`
2. 参考 [Sqlite版命令](https://github.com/cooderl/wewe-rss#sqlite) 部署好 WeWe Rss
3. 启动 wewe-rss-extensions，`DATABASE_URL`和`DATABASE_TYPE`与wewe-rss容器的配置保持对应，**确保可以共享到wewe-rss.db**

```sh
docker run -d \
  --name wewe-rss-extensions \
  -e DATABASE_TYPE=sqlite \
  -e DATABASE_URL="file:../data/wewe-rss.db" \
  -v $(pwd)/data:/app/data \
  wynying92/wewe-rss-extensions:latest
```

#### Mysql版

1. 参考 [扩展组件配置](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docs/configuation.md) 完成相关组件的配置，yaml配置文件放在目录 `$(pwd)/data/conf/`
2. 参考 [Mysql版命令](https://github.com/cooderl/wewe-rss#mysql) 部署好 WeWe Rss
3. 启动 wewe-rss-extensions，`network` `DATABASE_URL`和`DATABASE_TYPE`与wewe-rss容器的配置保持对应，**确保可以共享mysql数据库**

```sh
docker run -d \
  --name wewe-rss-extensions \
  -e DATABASE_TYPE=mysql \
  -e DATABASE_URL='mysql://root:123456@db:3306/wewe-rss?schema=public&connect_timeout=30&pool_timeout=30&socket_timeout=30' \
  -v $(pwd)/data:/app/data \
  --network wewe-rss \
  wynying92/wewe-rss-extensions:latest
```

## License

[MIT](https://raw.githubusercontent.com/wyn-ying/wewe-rss-extensions/main/LICENSE) @wyn-ying
