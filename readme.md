### 基于js逆向的极验滑动验证7.8.1

截至2021.06.01，应该是最新版本(7.8.1)的滑动验证码了，代码完成度并不高，只是实现了调用，并没用将代码完全抽离出来和去除冗余代码，但是相较于selenium模拟拖动还是方便了不少，不同的网站只需要替换该网站对应的极验token(即gt值)即可。
### 环境准备
```shell script
npm install canvas jsdom
```

- 某站的注册相关请求
![test](http://bbs.nightteam.cn/upload/tmp/1239_8VK78YD5NNME3BD.gif)

### 捐赠
如果你觉得项目帮助到您，请认真考虑请作者喝一杯咖啡 😄
| 微信二维码 | 支付宝二维码 |
| -------- | ---------- |
| <img src="https://github.com/coder-fly/geetest_reverse/blob/master/assets/wechat.jpg" width="200" height="200" alt="wechat-code"/><br/> | <img src="https://github.com/coder-fly/geetest_reverse/blob/master/assets/alipay.jpg" width=220px alt="alipay-code"> |

### License
MIT [©coder-fly](https://github.com/coder-fly)
