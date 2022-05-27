from pprint import pprint
from enum import Enum

from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient import errors


class AccountType(str, Enum):
    USER = "user"
    GROUP = "group"
    ServiceAccount = "serviceAccount"
    Domain = "domain"


SCOPES = ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/cloudplatformprojects']
SERVICE_ACCOUNT_FILE = '/meshcloud-project-test.json'


class GCPSDKObject:
    @classmethod
    def get_service_client(cls, service_name="cloudresourcemanager", version="v3"):
        """
        获取 客户端
        :param service_name:
        :param version:
        :return:
        """
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = discovery.build(service_name, version, credentials=credentials)
        return service

    def get_projects_iam_policy(self, project_name: str):
        """
        获取 project 层级的 iam policy
        :param project_name:
        :return:
        """
        service = self.get_service_client("cloudresourcemanager", "v3")
        resource_name = f"projects/{project_name}"
        request = service.projects().getIamPolicy(resource=resource_name)
        try:
            response = request.execute()
            return response
        except errors.HttpError as err:
            raise err

    def set_projects_iam_policy(self, project_name: str, bindings: list, audit_configs: list, etag: str):
        """
        设置 project 层级的 iam policy
        特别注意： 参数可以为空, 会清除所有角色权限!
        #  very important, please be careful !!
        :param project_name:
        :param bindings:
        :param audit_configs:
        :param etag:
        :return:
        """
        assert bindings is not None and len(bindings) > 0
        assert etag is not None and len(etag) > 0

        service = self.get_service_client("cloudresourcemanager", "v3")

        resource_name = f"projects/{project_name}"

        body = {
            "policy": {
                "bindings": bindings,
                "auditConfigs": audit_configs,
                "etag": etag,
                "version": 3
            }
        }
        request = service.projects().setIamPolicy(resource=resource_name, body=body)
        try:
            response = request.execute()
            return response
        except errors.HttpError as err:
            raise err


def add_iam_policy_binding(project_name: str, role_name: str, member_name: str, account_type: str):
    """
    在指定的 project 下的 role 里添加 user账户 或者 service_account账户

    操作步骤：
    1. 列出 project 下的IamPolicy
    2. 遍历bindings 在已经存在的role里增加账户，否则就新创建role 并添加账户
    3. 回填 project 下的IamPolicy  特别注意： Google 参数可以为空, 会清除所有角色权限!

    :param project_name: 项目名称或者项目id
    :param role_name: 角色名称
    :param member_name: 添加的账户名称
    :param account_type 账户类型
    The principal to add the binding for. Should be of the form user|group|serviceAccount:email or domain:domain.
    Examples: user:test-user@gmail.com, group:admins@example.com, serviceAccount:test123@example.domain.com, or domain:example.domain.com
    :return:
    """
    assert account_type in AccountType._value2member_map_

    role_name = role_name.strip()
    project_name = project_name.strip()
    member_name = member_name.strip()

    member_name = "{}:{}".format(account_type, member_name)

    gcp_sdk_obj = GCPSDKObject()
    projects_iam_policy = gcp_sdk_obj.get_projects_iam_policy(project_name)
    if not projects_iam_policy:
        raise Exception("not found iam_policy in project:{}".format(project_name))

    assert "etag" in projects_iam_policy
    assert "bindings" in projects_iam_policy

    bindings = projects_iam_policy.get('bindings')

    is_new_role_flag = True
    for binding in bindings:
        role = binding.get('role')
        if role == role_name:
            is_new_role_flag = False
            members = binding.get('members')
            if member_name in members:
                raise Exception(f"project:{project_name} members:{member_name}  already in role:{role} ")
            members.append(member_name)
            break

    if is_new_role_flag:
        bindings.append({"role": role_name,
                         "members": [member_name]})

    etag = projects_iam_policy.get('etag')
    auditConfigs = projects_iam_policy.get('auditConfigs', [])

    res = gcp_sdk_obj.set_projects_iam_policy(project_name=project_name,
                                              bindings=bindings,
                                              audit_configs=auditConfigs,
                                              etag=etag)

    return res


if __name__ == '__main__':
    gso = GCPSDKObject()

    # 获取 projects iam policy
    x = gso.get_projects_iam_policy("meshcloud-project")
    pprint(x)

    # 给 服务账户 添加 role
    y = add_iam_policy_binding("meshcloud-project", "roles/resourcemanager.projectIamAdmin", "yangwentao-test-service-key@meshcloud-project.iam.gserviceaccount.com", AccountType.ServiceAccount.value)
    pprint(y)

    # 给 用户账户 添加 role
    y = add_iam_policy_binding("meshcloud-project", "roles/viewer", "yangwentao@yunion-hk.com", AccountType.USER.value)
    pprint(y)

