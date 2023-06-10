# HMCP (help-my-class-please)

## 简介

用于自动化网课登录的 python 程序。

支持软件：腾讯会议、腾讯课堂。  
支持平台：windows7 及以上。

## 演示

![demo](img/demo.png)

## 运行方式

1. 建立虚拟环境并安装依赖项，以 `conda`、环境命名为 `class` 为例。

   ```shell
   conda create -n class python=3.9
   conda activate class
   pip install -r requirements.txt
   # or you can use: conda install --file requirements.txt
   ```

2. 运行（或双击）`init-and-make-shortcut.bat`。

   > 这一步会在桌面生成 `HMCP.lnk` 链接，指向 `config/my-run-hmcp.bat`。  
   > `config/my-run-hmcp.bat` 会使用 `config/my-class.json` 作为课程配置，见配置方式。

3. 双击桌面的 `HMCP`，看看是否能成功运行。

   > 如果你没有使用 conda、使用的 conda 环境不叫 class、使用了别的 . json，请自行修改 `config/my-run-hmcp.bat`。

4. 如果要一直运行，需要后台常开且电脑不能进入睡眠模式。

## 配置方式

- 仅需配置 `config/my-class.json`

  ```json
  {
  "path": {
      "腾讯会议": "C:/Program Files (x86)/Tencent/WeMeet/wemeetapp.exe",     // 你的安装路径
      "腾讯课堂": "C:/Program Files (x86)/Tencent/EDU/bin/TXEDU.exe"
  },
  "class": [
      {
          "name": "泡面的艺术",                // 课程名称
          "platform": "腾讯会议",              // 平台（目前支持腾讯会议和腾讯课堂）
          "detail": {                         // 详细信息，包括网址、会议号、会议密码、入会名称
              "url": "",
              "id": "123-4567-8901",
              "passwd": "12345",
              "myname": "3141592653-张三",
              "auto_close_audio": true        // 自动静音，默认为 true
          },
          "weekday": [1, 3, 5],               // 上课的星期
          "time": "8:30",                     // 课程开始时间
          "time_range": [-5, 15],             // 允许登录的时间范围
                                              //（提前5分钟或者推迟15分钟的范围内，如果还没登录就会登录）
          "time_lasting": 100                 // 课程时长
      },
      {
          "name": "睡大觉",
          "platform": "腾讯课堂",
          "detail": {
              "using": "url",                 // 课堂登录方式（目前还仅支持 url 网页登录）
              "url": "https://ke.qq.com/webcourse/1234567/123456789#taid=12345678901234567&lite=1"
          },
          "weekday": [1, 2, 3, 4, 5, 6, 7],
          "time": "10:30",
          "time_range": [-99999, 99999],
          "time_lasting": 30
      }
  ]
  }
  ```

## 开发者调试

- 通常直接运行 `helpMyClassPlease.py`。

  ```shell
  python ..\client\helpMyClassPlease.py
  ```
  
  如果要自行使用参数（如重新指定 class.json 路径、启动测试时间），可以使用
  
  ```shell
  python ..\client\helpMyClassPlease.py -j "class.json"
                               # or use: --json "class.json"
  python ..\client\helpMyClassPlease.py -t "[10, 2, 499]"
                               # or use: --test "[10, 2, 499]"
  ```
  
  其中测试时间的三个值分别为：每分钟的秒数、当前星期、当前距离 0:00 的分钟数。这两个参数可以同时添加。

## 待办

腾讯课堂目前只能采用网页版本

- [x] 提供自选命令行参数
- [x] 架构重构
- [x] 自动静音
- [ ] 客户端和网页版自主选择
- [x] 腾讯课堂自动签到
- [ ] 其他网课软件的支持
- [ ] 不需要常开也能运行（或者自动阻止睡眠模式）
