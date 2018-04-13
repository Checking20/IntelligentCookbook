# IntelligentCookbook 接口文档

## 全局约定：
	返回值形式：{status:(请求的状态),message:(一个简单短语解释状态码),data:{返回的数据object}}
	状态码： 200表示请求成功
		300 表示请求失败
		400 表示没有权限
	所有涉及到分页的URL，统一请求参数：
		page:第几页
		rows：每页多少个
	所有返回有/无的接口，返回值统一是{success:m} m可取值为0，1 其中0代表失败1代表成功
	全局约定中声明好的返回数据，在本文档中具体接口中留空
-----------------------------------------------------------------------------


# 用户相关
统一使用/user前缀
## 登录
	url:user/login
	method:POST
	paras:{"username":用户名,"password":密码}
	return:
	"message":
	1."用户名不存在"
	2."密码错误"
	"data":null

## 用户名是否已被占用
	url:user/existence/username
	method:GET
	paras:{"username":用户名}
	return:
	"message":
	1."用户名可用"
	2."用户名已注册"
	"data":null

## 邮箱是否已被占用
	url:user/existence/email
	method:GET
	paras:{"email":邮箱}
	return:
	"message":
	1."邮箱可用"
	2."邮箱已注册"
	"data":null

## 注册
	url:user/register
	method:POST
	paras:{"username":用户名,"password":密码,"email":邮箱}
	return:
	"message":
	1."注册成功"
	2."注册失败"
