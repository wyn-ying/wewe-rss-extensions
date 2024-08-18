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

- 支持多个同类型/不同类型的定时通知机器人，示例中为两个飞书机器人和一个钉钉机器人

- 支持为每个机器人设置独立的通知周期，分钟粒度

## 部署

### Docker Compose

1. 参考 [扩展组件配置](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docs/configuation.md) 完成相关组件的配置，yaml配置文件放在目录 `$(pwd)/data/conf/`
   - v0.2.0支持通过 `http://localhost:4100` 动态配置并保存（如果使用动态配置，则跳过第1步，待compose启动后进入页面完成配置）
2. 按需调整 docker compose yaml 文件
- Sqlite版参考 [docker-compose.sqlite.yml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docker-compose.sqlite.yml)
- Mysql版参考 [docker-compose.yml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docker-compose.yml)
3. 启动 docker compose

> [!NOTE]
> v0.2.0支持通过 `http://localhost:4100` 动态配置并保存
> <br>如需暴露到公网环境，建议在使用页面动态配置后，**保存配置**，停止并移除 extensions `docker compose down extensions`
> <br>之后将 docker-compose yaml 文件中的 extensions 修改为不对外映射 port，再重新启动 `docker-compose up -d extensions`
> <br>重启时会加载已保存的yaml配置文件

### Docker

#### Sqlite版

1. 参考 [扩展组件配置](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docs/configuration.md) 完成相关组件的配置，yaml配置文件放在目录 `$(pwd)/data/conf/`
   - v0.2.0支持通过 `http://localhost:4100` 动态配置并保存（如果使用动态配置，则跳过第1步，待compose启动后进入页面完成配置）
   - 公网环境下使用，建议参考[docker-compose](https://github.com/wyn-ying/wewe-rss-extensions#docker-compose)中的Note
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

1. 参考 [扩展组件配置](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/docs/configuration.md) 完成相关组件的配置，yaml配置文件放在目录 `$(pwd)/data/conf/`
   - v0.2.0支持通过 `http://localhost:4100` 动态配置并保存（如果使用动态配置，则跳过第1步，待compose启动后进入页面完成配置）
   - 公网环境下使用，建议参考[docker-compose](https://github.com/wyn-ying/wewe-rss-extensions#docker-compose)中的Note
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
