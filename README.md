# google-cloud-resource-manager
GCP Project 新增 用户账户 或 服务账户

### 功能
使用API接口，向GCP平台指定的project的role下，新增加用户账户或者服务账户


### 外部依赖包
* Python version: 3.8
* google-api-python-client version 2.49.0
* google-auth version: 2.6.6
* google-auth-oauthlib version: 0.5.1
* google-auth-httplib2 version: 0.1.0


### cloudresourcemanager API
* getIamPolicy 方法获取当前project 下的全部 role和members
* setIamPolicy 方法，将最新的 bindings 更新后的值进行重置  特别注意： 参数可以为空, 会清除所有角色权限!  very important, please be careful !!

### 执行步骤
1. 安装客户端库
```shell
pip install --upgrade google-api-python-client google-auth  google-auth-oauthlib google-auth-httplib2
```

2. 生成一个 service account
* 需要设置权限为 
![image](https://user-images.githubusercontent.com/10955940/170627536-e28295e5-d1d4-486b-b36c-ef0e9865c128.png)

3. 设置常量 
* SCOPES = ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/cloudplatformprojects']
* SERVICE_ACCOUNT_FILE = '/meshcloud-project-test.json'

4. 修改参数并执行脚本
> 参考 main.py中的列子


### 注意事项
- Calling this method requires enabling the App Engine Admin API.
- Google setIamPolicy 方法参数可以为空，会清除所有角色权限


### Authorization Scopes
Requires one of the following OAuth scopes:
- https://www.googleapis.com/auth/cloud-platform
- https://www.googleapis.com/auth/cloudplatformprojects


### 参考资料
- https://cloud.google.com/resource-manager/docs/apis
- https://cloud.google.com/resource-manager/reference/rest/v3/projects/getIamPolicy
- https://cloud.google.com/resource-manager/reference/rest/v3/projects/setIamPolicy
