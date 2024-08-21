# 扩展组件配置

完整示例参考 [conf_example.yaml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/conf_example.yaml)

> [!NOTE]
> v0.2.0之后支持通过 `http://localhost:4100` 动态配置并保存
> <br>如需暴露到公网环境，建议在使用页面动态配置后，**保存配置**，停止并移除容器。以docker compose 为例 `docker compose down extensions`
> <br>之后将容器修改为不对外映射port，再重新创建容器。以docker compose 为例 `docker-compose up -d extensions`
> <br>重启时会加载已保存的yaml配置文件

## 定时通知机器人配置

### 基础参数

- **default_interval_minutes**: Notifier默认的通知周期，单位：分钟，优先级高于环境变量中的`NOTIFY_INTERVAL_MINUTES`。如果缺省，会使用环境变量`NOTIFY_INTERVAL_MINUTES`
- **db_provider**: 数据库类型，优先级高于环境变量中的`DATABASE_TYPE`。如果缺省，会使用环境变量`DATABASE_TYPE`
- **db_url**: 数据库连接地址，优先级高于环境变量中的`DATABASE_URL`。如果缺省，会使用环境变量`DATABASE_URL`

### Notifier参数

- **notifiers**: Notifiers配置项，支持以列表形式配置多个Notifier

  > 举例: (摘自[conf_example.yaml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/conf_example.yaml))
  > ``` yaml
  > ...
  > notifiers:
  > - cls: FeishuNotifier
  >   name: feishu1
  >   interval_minutes: 10
  >   fs_token: xxxx
  > - cls: FeishuNotifier
  >   interval_minutes: 60
  >   fs_token: yyyy
  > - cls: DingtalkNotifier
  >   name: dingtalk1
  >   access_token: xxxx
  >   secret: xxxx
  > ...
  > ```
  > 含义是，设置3个Notifier：
  > - 第1个飞书通知机器人，每10分钟检测一次
  > - 第2个飞书通知机器人，每60分钟检测一次
  > - 第3个钉钉通知机器人，使用默认的检测周期

#### Notifiers中每个Notifier的通用参数

- **notifier.cls**: (*Required*) 要使用的Notifier类，包括FeishuNotifier（飞书通知机器人）、DingtalkNotifier（钉钉通知机器人），以及其他自定义机器人
- **notifier.name**: 服务启动发送测试消息时，用于确认连通性的Notifier名称，缺省则为cls同名
- **notifier.interval_minutes**: 本Notifier使用的通知周期，单位：分钟。优先级高于**default_interval_minutes**

#### FeishuNotifier（飞书通知机器人）特定参数

- **notifier.fs_token**: (*Required*) 飞书自定义机器人webhook中最后一段，形如`4e31c97f-c675-xxxx-xxxx-xxxxxxxxxx`，参考创建机器人时的完成页面

#### DingtalkNotifier（钉钉通知机器人）特定参数

- **notifier.access_token**: (*Required*) 钉钉机器人的`access_token`，参考创建机器人时的设置页面
- **notifier.secret**: (*Required*) 钉钉机器人的`secret`，参考创建机器人时的设置页面

### 自定义机器人

1. 参考[notifier.py](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/src/model/notifier.py)，继承`BaseNotifier`并实现`config_params_is_valid()` `generate_message()` `_send()`三个方法（必须）以及其他想要修改的方法
2. 提交PR  or  自行build docker镜像
3. 在conf.yaml的**notifiers**中增加一个Notifier配置，cls使用自定义机器人的类名

## 个性化更新配置

### 基础参数

- **wewerss_origin_url**: (*Required*) WeWe Rss的源url，优先级高于环境变量中的`WEWERSS_ORIGIN_URL`。如果缺省，会使用环境变量`WEWERSS_ORIGIN_URL`

### Cron参数

- **crons**: Cron配置项，支持以Dict[str, List[str]]形式，为配置多个公众号配置Cron表达式。每个公众号可以配置多个Cron表达式，满足任意一个即触发更新。

  > 举例: (摘自[conf_example.yaml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/conf_example.yaml))
  > ``` yaml
  > ...
  > crons:
  >   MP_WXS_123:
  >   - 45 22 * * 1-5
  >   - 20 18 * * 6
  >   MP_WXS_456:
  >   - 5 9 * * 1-5
  > ...
  > ```
  > 含义是，为两个公众号单独设置更新时间：
  > - 当 `45 22 * * 1-5` 和 `20 18 * * 6` 有一个Cron满足时，更新 `MP_WXS_123` 公众号
  > - 当 `5 9 * * 1-5` Cron满足时，更新 `MP_WXS_456` 公众号

  > [!NOTE]
  > 为了降低封号风险，个性化更新限制了触发频率，每分钟最多触发2次
