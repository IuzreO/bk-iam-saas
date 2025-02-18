# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
"""
蓝鲸平台提供的公用方法

#===============================================================================
# 1.页面输入内容转义（防止xss攻击）
from common.utils import html_escape, url_escape

 # 转义html内容
 html_content = html_escape(input_content)

 # 转义url内容
 url_content = url_escape(input_content)
#===============================================================================
"""
from .pxfilter import XssHtml


def html_escape(str_escape, fromtype=0, is_json=False):
    """
    字符串转义为html代码
    @param str_escape: 需要解析的html代码
    @param fromtype: 来源，0：views函数，1：middleware
    @param is_json: 是否为json串
    """
    try:
        result_str = escape_new(str_escape, fromtype, is_json)
        return result_str
    except Exception:  # pylint: disable=broad-except
        return str_escape


def url_escape(url_escape):
    """
    转义url中的特殊字符
    @param str_escape: 需要解析的url
    """
    try:
        result_str = escape_url(url_escape)
        return result_str
    except Exception:  # pylint: disable=broad-except
        return url_escape


def html_escape_name(str_escape):
    """
    字符串转义为html代码
    @param str_escape: 需要解析的html代码
    """
    try:
        result_str = escape_name(str_escape)
        return result_str
    except Exception:  # pylint: disable=broad-except
        return str_escape


def escape_url(s):
    s = s.replace("<", "")
    s = s.replace(">", "")
    s = s.replace(' ', "")
    s = s.replace('"', "")
    s = s.replace("'", "")
    return s


def escape_name(s):
    '''Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.
    rewrite the cgi method
    '''
    s = s.replace("&", "")  # Must be done first!
    s = s.replace("<", "")
    s = s.replace(">", "")
    s = s.replace(' ', "")
    s = s.replace('"', "")
    s = s.replace("'", "")
    return s


def check_script(str_escape):
    """
    防止js脚本注入
    @param str_escape: 要检测的字符串
    @param fromtype: 0：views，1：middleware
    """
    try:
        parser = XssHtml()
        parser.feed(str_escape)
        parser.close()
        return parser.getHtml()
    except Exception:  # pylint: disable=broad-except
        return str_escape


def escape_new(s, fromtype, is_json):
    '''Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.
    rewrite the cgi method
    @param fromtype: 来源，0：views函数，1：middleware（对&做转换），默认是0
    @param is_json: 是否为json串（True/False
    '''
    # &转换
    if fromtype == 1 and not is_json:
        s = s.replace("&", "&amp;")
    # <>转换
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    # 单双引号转换
    if not is_json:
        s = s.replace(' ', "&nbsp;")
        s = s.replace('"', "&quot;")
        s = s.replace("'", "&#39;")
    return s
