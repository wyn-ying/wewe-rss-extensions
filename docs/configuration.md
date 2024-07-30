# 扩展组件配置

## 定时通知机器人配置

完整示例参考 [notify_example.yaml](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/notify_example.yaml)

### 主要参数
- **default_interval_minutes**: (*Optional*) Notifier默认的通知周期，单位：分钟，优先级高于环境变量中的`NOTIFY_INTERVAL_MINUTES`。如果缺省，会使用环境变量`NOTIFY_INTERVAL_MINUTES`
- **db_provider**: (*Optional*) 数据库类型，优先级高于环境变量中的`DATABASE_TYPE`。如果缺省，会使用环境变量`DATABASE_TYPE`
- **db_url**: (*Optional*) 数据库连接地址，优先级高于环境变量中的`DATABASE_URL`。如果缺省，会使用环境变量`DATABASE_URL`
- **notifiers**: (*Required*) Notifiers配置项，支持以列表形式配置多个Notifier

#### Notifiers中每个Notifier的通用参数
- **cls**: (*Required*) 要使用的Notifier类，包括FeishuNotifier（飞书通知机器人）、DingtalkNotifier（钉钉通知机器人），以及其他自定义机器人
- **name**: (*Optional*) 服务启动发送测试消息时，用于确认连通性的Notifier名称，缺省则为cls同名
- **interval_minutes**: (*Optional*) 本Notifier使用的通知周期，单位：分钟。优先级高于**default_interval_minutes**

#### FeishuNotifier（飞书通知机器人）特定参数
- **fs_token**: (*Required*) 飞书自定义机器人webhook中最后一段，形如`4e31c97f-c675-xxxx-xxxx-xxxxxxxxxx`，参考创建机器人时的完成页面

#### DingtalkNotifier（钉钉通知机器人）特定参数
- **access_token**: (*Required*) 钉钉机器人的`access_token`，参考创建机器人时的设置页面
- **secret**: (*Required*) 钉钉机器人的`secret`，参考创建机器人时的设置页面

### 自定义机器人
1. 参考[notifier.py](https://github.com/wyn-ying/wewe-rss-extensions/blob/main/src/notifier.py)，继承`BaseNotifier`并实现`config_params_is_valid()` `generate_message()` `_send()`三个方法（必须）以及其他想要修改的方法
2. 提交PR  or  自行build docker镜像
3. 在notify.yaml的**notifiers**中增加一个Notifier配置，cls使用自定义机器人的类名