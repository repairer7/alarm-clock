# Alarm Clock

基于 GitHub Actions 和 Bark 推送的智能闹钟项目。

项目可以根据中国节假日和调休安排，自动判断当天是否为工作日，并通过 Bark 向手机发送提醒。同时支持通勤时间检测和午休提醒，适合需要固定上下班、通勤距离较远或容易错过午休时间的用户。

## 功能特性

- 根据中国法定节假日和调休安排判断是否为工作日
- 工作日自动发送 Bark 闹钟提醒
- 调用百度地图 API 获取驾车通勤时间
- 当预计通勤时间超过 40 分钟时发送提醒
- 根据当前位置与工作地点的距离发送午休提醒
- 支持通过配置文件统一开启或关闭闹钟
- 使用 GitHub Actions 定时或手动运行，无需额外服务器

## 项目结构

```text
.
├── .github/
│   └── workflows/
│       ├── Commute.yml       # 通勤时间检测
│       ├── Workday.yml       # 工作日闹钟
│       └── Siesta.yml        # 午休提醒
├── commute.py                # 通勤时间检测脚本
├── workday.py                # 工作日提醒脚本
├── siesta.py                 # 午休提醒脚本
├── distance.json             # 距离配置
└── whetheralarm.json         # 闹钟总开关
```

## 工作原理

### 工作日提醒

`workday.py` 使用 `chinese_calendar` 判断当天是否为中国工作日，包括调休工作日。

如果当天是工作日，并且 `whetheralarm.json` 中的开关不是 `no`，程序会通过 Bark 发送持续响铃提醒。

### 通勤提醒

`commute.py` 的执行流程如下：

1. 判断当天是否为工作日
2. 读取出发地和目的地
3. 调用百度地图地理编码接口获取坐标
4. 调用百度地图驾车路线接口获取预计通勤时间
5. 当通勤时间超过 40 分钟时，通过 Bark 发送提醒

### 午休提醒

`siesta.py` 会判断当天是否为工作日，并读取 `distance.json`。

当配置的距离小于 `1` 时，程序会发送午休提醒。

## 使用方法

### 1. Fork 仓库

点击仓库右上角的 **Fork**，将项目复制到自己的 GitHub 账号下。

### 2. 配置 GitHub Secrets

进入仓库：

```text
Settings → Secrets and variables → Actions → New repository secret
```

添加以下 Secrets：

| 名称 | 说明 | 示例 |
| --- | --- | --- |
| `BARK_HOST` | Bark 服务域名，不需要填写协议 | `api.day.app` |
| `BARK_KEY` | Bark 推送设备 Key | `xxxxxxxxxxxxxxxx` |
| `BAIDU_AK` | 百度地图开放平台 AK | `your-baidu-ak` |
| `ORIGIN_ADDR` | 通勤出发地址 | `北京市朝阳区某小区` |
| `DESTINATION_ADDR` | 通勤目的地址 | `北京市海淀区某公司` |

注意：

- `BARK_KEY`、`BAIDU_AK` 等敏感信息不要直接写入代码
- `BARK_HOST` 建议只填写域名，例如 `api.day.app`
- 百度地图 AK 需要开通地理编码和路线规划相关 API

### 3. 配置闹钟开关

编辑 `whetheralarm.json`：

```json
{
  "whetheralarm": "yes"
}
```

开启提醒：

```json
{
  "whetheralarm": "yes"
}
```

关闭提醒：

```json
{
  "whetheralarm": "no"
}
```

当值为 `no` 时，工作日提醒和通勤检测都会跳过。

### 4. 配置午休距离

编辑 `distance.json`：

```json
{
  "distance": 0.46
}
```

当 `distance` 小于 `1` 时，午休脚本会发送 Bark 提醒；当距离大于或等于 `1` 时，不发送提醒。

距离的具体含义取决于写入该文件的计算逻辑，建议统一使用公里作为单位。

可配合iPhone快捷指令，定时获取所在位置与午休点距离，若因出差等原因远离午休地点，则不发送提醒。

### 5. 手动运行 GitHub Actions

进入仓库的：

```text
Actions
```

选择需要运行的工作流：

- `Workday Check`：发送工作日提醒
- `Commute Check`：检测通勤时间
- `Siesta Check`：检测午休提醒

点击：

```text
Run workflow
```

即可手动执行。

## 本地运行

安装 Python 3.11 或更高版本：

```bash
pip install requests chinese_calendar
```

配置环境变量。

Linux/macOS：

```bash
export BARK_HOST="api.day.app"
export BARK_KEY="your-bark-key"
export BAIDU_AK="your-baidu-ak"
export ORIGIN_ADDR="出发地址"
export DESTINATION_ADDR="目的地址"
```

Windows PowerShell：

```powershell
$env:BARK_HOST="api.day.app"
$env:BARK_KEY="your-bark-key"
$env:BAIDU_AK="your-baidu-ak"
$env:ORIGIN_ADDR="出发地址"
$env:DESTINATION_ADDR="目的地址"
```

运行脚本：

```bash
python workday.py
python commute.py
python siesta.py
```

## 注意事项

- 当前 GitHub Actions 工作流使用 `workflow_dispatch`，默认需要手动点击运行
- GitHub Actions 的时间应以 UTC 为基础配置，项目运行环境设置为 `Asia/Shanghai`
- 百度地图 API 可能存在调用频率限制
- Bark 推送依赖网络连接和正确的设备 Key
- `whetheralarm.json` 和 `distance.json` 的修改需要提交到仓库后，GitHub Actions 才能读取到最新配置
- 请妥善保管 GitHub Secrets，避免将密钥写入公开代码

## 技术栈

- Python
- GitHub Actions
- Bark
- 百度地图开放平台
- `chinese_calendar`
- `requests`

## 许可证

本项目暂未指定开源许可证。若要允许他人明确使用、修改和分发代码，建议根据需要添加 MIT、Apache-2.0 等许可证。
