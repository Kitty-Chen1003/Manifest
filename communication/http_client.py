import json
import requests
from utils import db, signature
import xml.dom.minidom

from utils.path import get_resource_path


def read_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config


# 获取日志文件路径
log_path = get_resource_path("config/config.json")
url = read_config(log_path)['api']['base_url']


# 登录以获取 Token
def get_token(username, password, user_type):
    try:
        # 发送POST请求
        response = requests.post(url + '/users/login',
                                 json={'username': username, 'password': password, 'type': user_type})

        if response.json().get('state') == 200:
            # 尝试解析返回的JSON数据
            try:
                response_data = response.json()
                return response_data.get('data')['access_token']  # 使用 .get() 避免键错误
            except ValueError:
                print("Error: Response is not valid JSON")
                return None
        else:
            print(f"Login failed, status code: {response.status_code}")
            print(response.text)  # 打印详细的错误响应
            return None

    except requests.exceptions.RequestException as e:
        # 捕获所有请求相关的异常
        print(f"Request failed: {e}")
        return None


def change_password(token, username, password):
    headers = {'Authorization': f'Bearer {token}'}

    data = {
        'username': username,
        'password': password
    }

    try:
        # 发送 POST 请求到 change_password 路由
        response = requests.post(url + '/users/change_password', json=data, headers=headers)

        # 检查响应的状态码
        if response.json().get('state') == 200:
            print("Password change successful.")
            return response.json().get('state')  # 你可以返回状态码或其他信息

        # 如果状态码不是 200，打印详细的错误信息
        else:
            print(f"Failed to change password. Status code: {response.status_code}")
            print(f"Response: {response.text}")  # 打印错误响应内容
            return response.json().get('state')

    except requests.exceptions.RequestException as e:
        # 捕获所有请求相关的异常，如网络连接问题、超时等
        print(f"Request failed: {e}")
        return None


def add_user(token, username, remark):
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'username': username,
        'remark': remark
    }

    try:
        # 发送 POST 请求到 add_user 路由
        response = requests.post(url + '/users/add_user', json=data, headers=headers)

        # 检查响应的状态码
        if response.json().get('state') == 200:
            print("User added successfully.")
            return response.json().get('state')  # 可以返回状态码或其他有用的信息

        # 如果状态码不是 200，打印详细的错误信息
        else:
            print(f"Failed to add user. Status code: {response.status_code}")
            print(f"Response: {response.text}")  # 打印错误响应内容
            return response.json().get('state')

    except requests.exceptions.RequestException as e:
        # 捕获所有请求相关的异常，如网络连接问题、超时等
        print(f"Request failed: {e}")
        return None


def delete_user(token, username):
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'username': username
    }

    try:
        # 发送 POST 请求到 delete_user 路由
        response = requests.post(url + '/users/delete_user', json=data, headers=headers)

        # 检查响应的状态码
        if response.json().get('state') == 200:
            print("User deleted successfully.")
            return response.json().get('state')  # 返回状态码或其他有用信息

        # 如果状态码不是 200，打印详细的错误信息
        else:
            print(f"Failed to delete user. Status code: {response.status_code}")
            print(f"Response: {response.text}")  # 打印错误响应内容
            return response.json().get('state')

    except requests.exceptions.RequestException as e:
        # 捕获所有请求相关的异常，如网络连接问题、超时等
        print(f"Request failed: {e}")
        return None


def get_all_user(token):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        # 发送 GET 请求到 get_all_user 路由
        response = requests.get(url + '/users/get_all_user', headers=headers)

        # 检查响应的状态码
        if response.json().get('state') == 200:
            try:
                # 尝试解析 JSON 数据
                response_data = response.json()
                # 检查返回的数据是否包含 'users_list'
                if 'data' in response_data:
                    return response_data['data'], response.json().get('state')
                else:
                    print("Error: 'users_list' not found in response")
                    return [], response.json().get('state')
            except ValueError:
                print("Error: Response is not valid JSON")
                return [], response.json().get('state')
        else:
            print(f"Failed to get users. Status code: {response.json().get('state')}")
            print(f"Response: {response.text}")  # 打印错误响应内容
            return [], response.json().get('state')

    except requests.exceptions.RequestException as e:
        # 捕获请求相关的异常，如网络连接问题、超时等
        print(f"Request failed: {e}")
        return [], None


def change_rabbitmq_settings(token, data):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        # 发送 POST 请求到 change_rabbitmq_settings 路由
        response = requests.post(url + '/change_rabbitmq_settings', json=data, headers=headers)

        # 检查响应的状态码
        if response.json().get('state') == 200:
            print("RabbitMQ settings changed successfully.")
            return response.json().get('state')  # 返回状态码或其他信息

        # 如果状态码不是 200，打印详细的错误信息
        else:
            print(f"Failed to change RabbitMQ settings. Status code: {response.status_code}")
            print(f"Response: {response.text}")  # 打印错误响应内容
            return response.json().get('state')

    except requests.exceptions.RequestException as e:
        # 捕获所有请求相关的异常，如网络连接问题、超时等
        print(f"Request failed: {e}")
        return None


def synchronize_data(token, username):
    try:
        # 获取当前用户的 active_main_id 列表
        active_main_id = db.get_active_main_id(username)

        # 请求体中的数据
        data = {
            'username': username,
            'active_main_ids': active_main_id
        }

        # 设置请求头，包含 JWT token
        headers = {'Authorization': f'Bearer {token}'}

        # 发送 GET 请求到 synchronize_data 路由
        response = requests.get(url + '/generate/synchronize_data', json=data, headers=headers)

        # 检查响应状态码
        if response.json().get('state') == 200:
            try:
                data = response.json().get('data')
                # 检查数据中是否包含所需的字段
                if all(key in data for key in ['MainExcelTable', 'SubExcelTable', 'SubExcelData', 'SubXMLData', 'SignatureForm']):
                    main_excel_data = data['MainExcelTable']
                    sub_excel_data = data['SubExcelTable']
                    sub_excel_data_table = data['SubExcelData']
                    sub_xml_data = data['SubXMLData']
                    signature_data = data['SignatureForm']

                    # 分别插入每张表的数据
                    db.insert_main_excel_table(main_excel_data)
                    db.insert_sub_excel_table(sub_excel_data)
                    db.insert_sub_excel_data(sub_excel_data_table)
                    db.insert_sub_xml_data(sub_xml_data, username)
                    db.synchronize_signature_form(signature_data)

                    print("Data synchronized successfully.")
                    return True
                else:
                    print("Error: Missing expected data fields in the response.")
                    return False
            except ValueError:
                # 捕获 JSON 解析错误
                print("Error: Response is not valid JSON.")
                return False
        else:
            # 如果状态码不是 200，打印详细的错误信息
            print(f"Failed to synchronize data: {response.json().get('state')}")
            print(f"Response: {response.text}")  # 打印错误响应内容
            return False
    except requests.exceptions.RequestException as e:
        # 捕获请求相关的异常，如网络连接问题、超时等
        print(f"Request failed: {e}")
        return False


# 上传 Excel 数据
def upload_excel_data(token, data, file_path, password, signature_information):
    headers = {'Authorization': f'Bearer {token}'}
    username = data['username']

    try:
        # 发送 POST 请求到 upload_zc415 路由
        response = requests.post(url + '/generate/upload_zc415', json=data, headers=headers)

        # 检查响应的状态码
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('state') == 200:
                datas = response_data.get('data')
                signed_datas = []
                index_main_id = ''
                datas_subid_lrn = []
                for data in datas:
                    try:
                        main_id = data['main_id']
                        sub_id = data['sub_id']
                        lrn = data['lrn']
                        xml_data = data['xml_data']
                        type = data['type']
                        message_id = data['message_id']

                        datas_subid_lrn.append([sub_id, lrn])
                        try:
                            signed_xml_data = signature.sign_xml(
                                xml_data.encode('utf-8'),
                                file_path,
                                password,
                                signature.SignedSignatureProperties(
                                    signer=signature_information['name'],
                                    phone=signature_information['phoneNumber'],
                                    email=signature_information['eMailAddress']
                                )
                            )
                        except Exception as e:
                            print(f"处理 XML 文件时出错: {e}")
                            return None, None
                        # 签名
                        signed_data = {
                            'main_id': main_id,
                            'sub_id': sub_id,
                            'xml_data': signed_xml_data.decode('utf-8'),
                            'lrn': lrn,
                            'type': type,
                            'message_id': message_id,
                            'signature_information': signature_information,
                            'direction': 'send'
                        }
                        signed_datas.append(signed_data)
                    except KeyError as e:
                        # 捕获缺少关键字段的异常
                        print(f"Missing key in data: {e}")
                        return None, None

                upload_data = {
                    'username': username,
                    'data': signed_datas
                }

                try:
                    # 发送签名后的数据
                    sign_response = requests.post(url + '/generate/sign_xml', json=upload_data,
                                                  headers=headers)

                    sign_response_data = sign_response.json()
                    if sign_response_data.get('state') == 200:
                        # message_id_list = sign_response_data.get('data')
                        # db.insert_signature_information(
                        #     message_id_list,
                        #     signature_information,
                        #     'send',
                        #     username
                        # )
                        print("Excel data uploaded successfully.")
                        return sign_response_data.get('state'), datas_subid_lrn  # 返回状态码，或者其他你需要的信息
                    else:
                        print(f"Failed to sign XML. Status code: {sign_response.status_code}")
                        print(f"Response: {sign_response.text}")
                        return None, None
                except requests.exceptions.RequestException as e:
                    # 捕获 sign_xml 请求中的异常
                    print(f"Sign XML request failed: {e}")
                    return None, None
            else:
                # 如果 state 不为 200，打印错误信息
                print(f"Failed to upload Excel data. State: {response_data.get('state')}")
                print(f"Response: {response_data}")
                return None, None
        else:
            print(f"Failed to upload Excel data. HTTP Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None

    except requests.exceptions.RequestException as e:
        # 捕获所有请求相关的异常，如网络连接问题、超时等
        print(f"Request failed: {e}")
        return None, None


# 检查状态
def check_status(token, data):
    username = data['username']
    headers = {'Authorization': f'Bearer {token}'}
    try:
        # 发送请求，携带 active_main_ids
        response = requests.get(url + '/generate/check_status', headers=headers, json=data)
        response.raise_for_status()  # 如果响应状态码是 4xx 或 5xx，将引发 httpsError

        # 假设服务器返回的 JSON 格式是一个列表，里面包含多个字典
        data_lists = response.json().get('data').get('data')
        signature_datas = response.json().get('data').get('signatureInfo')
        if data_lists:
            grouped_dict = {}

            # 按 sub_id 分组
            for item in data_lists:
                sub_id = item.get("sub_id")
                if sub_id not in grouped_dict:
                    grouped_dict[sub_id] = []
                grouped_dict[sub_id].append(item)

            # 转换为二维列表
            data_lists = list(grouped_dict.values())

            # 存储数据到数据库并确认消息
            if response.json().get('state') == 200:
                db.synchronize_signature_form(signature_datas)

                for data_list in data_lists:
                    sub_id = data_list[0].get('sub_id')
                    sub_id_datas = db.get_sub_table_data_by_id(sub_id)  # 获取本地已有数据

                    # 确保 sub_id_datas 中的字段和格式正确，转换为元组集合
                    existing_data_set = {
                        (
                            d.get("main_id"),
                            d.get("sub_id"),
                            d.get("type"),
                            d.get("event_time"),
                            d.get("direction"),
                            d.get("CR"),
                            d.get("messageID"),
                            json.dumps(d.get("json_data"), sort_keys=True),  # 将 json_data 转换为字符串并排序键
                        )
                        for d in sub_id_datas
                    }

                    for item in data_list:
                        main_id = item.get('main_id')
                        sub_id = item.get('sub_id')
                        type_value = item.get('type')
                        event_time = item.get('event_time')
                        direction = item.get('direction')
                        json_data = item.get('json_data')
                        cr = item.get('CR')
                        message_id = item.get('messageID')

                        # 如果该数据不存在于本地，存储数据
                        data_tuple = (
                            main_id,
                            sub_id,
                            type_value,
                            event_time,
                            direction,
                            cr,
                            message_id,
                            json.dumps(json_data, sort_keys=True),  # 转换为字符串并排序键
                        )
                        if data_tuple not in existing_data_set:
                            db.store_xml_data(main_id, sub_id, type_value, json_data, event_time, direction, username,
                                              cr, message_id)
                            db.update_sub_table(sub_id, new_event_time=event_time)

        return response.json().get('state')

    except requests.exceptions.HTTPError as https_err:
        print(f"https error occurred: {https_err}")
        return None  # 或者返回一个特定的错误消息
    except Exception as err:
        print(f"An error occurred: {err}")
        return None  # 或者返回一个特定的错误消息


# 确认消息
def confirm_message(token, server_xml_id, event_time, sub_table_id):
    headers = {'Authorization': f'Bearer {token}'}

    data = {
        'server_xml_id': server_xml_id,
        'sub_table_id': sub_table_id,
        'event_time': event_time
    }

    try:
        # 发送 POST 请求到 confirm_message 路由
        response = requests.post(url + '/generate/confirm_message',
                                 json=data, headers=headers)

        # 检查响应状态码是否是 200
        response.raise_for_status()  # 如果响应状态码是 4xx 或 5xx，将引发 httpsError

        try:
            # 解析 JSON 响应
            response_data = response.json()
            return response_data  # 返回解析后的 JSON 数据
        except ValueError:
            print("Error: Response is not valid JSON.")
            return None  # 如果响应体不是有效的 JSON 格式，返回 None

    except requests.exceptions.HTTPError as https_err:
        print(f"https error occurred: {https_err}")
        return None  # 如果发生 https 错误，返回 None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None  # 如果发生请求相关错误，返回 None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None  # 捕获所有其他类型的异常并返回 None


def upload_reply_message(token, data, file_path, password, signature_info=None):
    headers = {'Authorization': f'Bearer {token}'}
    username = data['username']
    try:
        # 发送 POST 请求到 upload_reply_message 路由
        response = requests.post(url + '/generate/upload_reply_message',
                                 json=data, headers=headers)

        # 检查响应状态码是否是 200
        response.raise_for_status()  # 如果响应状态码是 4xx 或 5xx，将引发 httpsError

        # 检查响应的状态码
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('state') == 200:
                datas = response_data.get('data')
                signed_datas = []
                index_main_id = ''
                if not signature_info:
                    signature_information = {}
                for data in datas:
                    try:
                        main_id = data['main_id']
                        sub_id = data['sub_id']
                        xml_data = data['xml_data']
                        type = data['type']
                        message_id = data['message_id']

                        def format_xml(xml_string):
                            """
                            格式化 XML 字符串为标准格式（带缩进）
                            :param xml_string: 原始的 XML 字符串
                            :return: 格式化后的 XML 字符串
                            """
                            # 使用 minidom 解析并格式化
                            dom = xml.dom.minidom.parseString(xml_string)
                            return dom.toprettyxml(indent="  ")
                        if type == 'upd':
                            xml_data = format_xml(xml_data)

                        if main_id != index_main_id:
                            index_main_id = main_id
                            if not signature_info:
                                signature_information = \
                                    db.get_main_table_data_by_sequence(index_main_id)['representative contact person'][
                                        0]
                            else:
                                signature_information = signature_info
                        try:
                            signed_xml_data = signature.sign_xml(
                                xml_data.encode('utf-8'),
                                file_path,
                                password,
                                signature.SignedSignatureProperties(
                                    signer=signature_information['name'],
                                    phone=signature_information['phoneNumber'],
                                    email=signature_information['eMailAddress']
                                )
                            )
                        except Exception as e:
                            print(f"处理 XML 文件时出错: {e}")
                            return 'error'

                        # 签名
                        signed_data = {
                            'main_id': main_id,
                            'sub_id': sub_id,
                            'xml_data': signed_xml_data.decode('utf-8'),
                            'type': type,
                            'message_id': message_id,
                            'signature_information': signature_information,
                            'direction': 'send'
                        }
                        signed_datas.append(signed_data)
                    except KeyError as e:
                        # 捕获缺少关键字段的异常
                        print(f"Missing key in data: {e}")
                        return None

                upload_data = {
                    'username': username,
                    'data': signed_datas
                }

                try:
                    # 发送签名后的数据
                    sign_response = requests.post(url + '/generate/sign_xml', json=upload_data,
                                                  headers=headers)
                    sign_response_data = sign_response.json()
                    if sign_response_data.get('state') == 200:
                        # message_id_list = sign_response_data.get('data')
                        # db.insert_signature_information(
                        #     message_id_list,
                        #     signature_information,
                        #     'send',
                        #     username
                        # )
                        print("Excel data uploaded successfully.")
                        return sign_response_data.get('state')  # 返回状态码，或者其他你需要的信息
                    else:
                        print(f"Failed to sign XML. Status code: {sign_response.status_code}")
                        print(f"Response: {sign_response.text}")
                        return None
                except requests.exceptions.RequestException as e:
                    # 捕获 sign_xml 请求中的异常
                    print(f"Sign XML request failed: {e}")
                    return None
            else:
                # 如果 state 不为 200，打印错误信息
                print(f"Failed to upload Excel data. State: {response_data.get('state')}")
                print(f"Response: {response_data}")
                return None

    except requests.exceptions.HTTPError as https_err:
        print(f"https error occurred: {https_err}")
        return None  # 如果发生 https 错误，返回 None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None  # 如果发生请求相关错误，返回 None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None  # 捕获所有其他类型的异常并返回 None


def get_xml(token, data):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        # 发送 GET 请求
        response = requests.get(url + '/generate/get_xml', headers=headers, json=data)

        # 检查响应状态码是否为 200
        response.raise_for_status()  # 如果响应状态码是 4xx 或 5xx，将引发 httpsError
        # 尝试解析响应的 JSON 数据
        try:
            if response.json().get('state') == 200:
                return response.json().get('data')  # 返回解析后的 JSON 数据
            else:
                return []
        except ValueError:
            print("Error: Response is not valid JSON.")
            return []  # 如果响应体不是有效的 JSON 格式，返回 None

    except requests.exceptions.HTTPError as https_err:
        print(f"https error occurred: {https_err}")
        return None  # 如果发生 https 错误，返回 None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None  # 如果发生请求相关错误，返回 None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None  # 捕获所有其他类型的异常并返回 None


def delete_corresponding_data_by_main_ids(token, data):
    headers = {'Authorization': f'Bearer {token}'}

    try:
        # 发送 POST 请求到指定路由
        response = requests.post(url + '/generate/delete_timed_out_data',
                                 json=data, headers=headers)

        # 检查响应状态码是否为 200
        response.raise_for_status()  # 如果状态码为 4xx 或 5xx，抛出 httpsError
        # 返回响应的状态码
        return response.json().get('state')

    except requests.exceptions.HTTPError as https_err:
        print(f"https error occurred: {https_err}")
        return None  # 如果发生 https 错误，返回 None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None  # 如果发生请求相关错误，返回 None
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
        return None  # 捕获所有其他类型的异常并返回 None
