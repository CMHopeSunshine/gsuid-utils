"""
MiniGG API v4/v5 请求模块。
参考：https://blog.minigg.cn/g/18
MiniGG Enka 加速服务不在此模块内。
"""
from __future__ import annotations

import warnings
from enum import Enum
from typing import Any, cast

from httpx import AsyncClient

from gsuid_utils.api.types import AnyDict
from gsuid_utils.api.minigg.exception import MiniggNotFoundError
from gsuid_utils.api.minigg.models import Weapon, WeaponCosts, WeaponStats

MINIGG_AUDIO_URL = "https://genshin.minigg.cn/"
MINIGG_URL = "https://info.minigg.cn"
MINIGG_MAP_URL = "https://map.minigg.cn/map/get_map"


class APILanguages(str, Enum):
    """API 语言列表"""

    CHS = "CN"
    """简体中文"""
    CN = "CN"
    """简体中文"""

    JP = "JP"
    """日语"""
    JA = "JP"
    """日语"""

    EN = "EN"
    """英语"""
    ENG = "EN"
    """英语"""

    KR = "KR"
    """韩语"""
    KA = "KR"
    """韩语"""

    CHT = "CHT"
    """繁体中文"""
    FR = "FR"
    """法语"""
    DE = "DE"
    """德语"""
    ID = "ID"
    """印度尼西亚语"""
    PT = "PT"
    """葡萄牙语"""
    RU = "RU"
    """俄语"""
    ES = "ES"
    """西班牙语"""
    TH = "TH"
    """泰语"""
    VI = "VI"
    """越南语"""


async def get_map_data(
    resource_name: str, map_id: str, is_cluster: bool = False
) -> bytes:
    """返回地图信息。

    Args:
        resource_name (str): 资源点名称。
        map_id (str): 地图ID。
        is_cluster (bool, optional): 是否使用 K-Means 聚类算法。 Defaults to False.

    Raises:
        MiniggNotFoundError: 资源未找到。

    Returns:
        bytes: 图片。
    """
    async with AsyncClient() as client:
        req = await client.get(
            url=MINIGG_MAP_URL,
            params={
                'resource_name': resource_name,
                'map_id': map_id,
                'is_cluster': is_cluster,
            },
        )
    if req.headers['content-type'] == 'image/jpeg':
        return req.content
    else:
        raise MiniggNotFoundError(**req.json())


async def get_audio_info(
    name: str, audio_id: str, language: str = 'cn'
) -> str:
    """`@deprecated: API is invalid` 访问 MiniGG API 获得原神角色音频信息。

    Args:
        name (str): 原神角色名称。
        audio_id (str): 语音id。
        language (str, optional): 语言。 Defaults to 'cn'.

    Returns:
        str: 语音 URL。
    """
    warnings.warn("Audio API is already deprecated.", DeprecationWarning)
    async with AsyncClient() as client:
        req = await client.get(
            url=MINIGG_AUDIO_URL,
            params={
                'characters': name,
                'audioid': audio_id,
                'language': language,
            },
        )
    return req.text


async def minigg_request(
    endpoint: str,
    query: str,
    query_languages: APILanguages = APILanguages.CHS,
    result_languages: APILanguages = APILanguages.CHS,
    match_categories: bool = False,
    **kwargs: Any,
) -> AnyDict | list[str]:
    """请求 MiniGG API。

    Args:
        endpoint (str): 终结点。
        query (str): 查询名称。
        query_languages (APILanguages, optional): 查询语言。
            Defaults to APILanguages.CHS.
        result_languages (APILanguages, optional): 返回语言。
            Defaults to APILanguages.CHS.
        match_categories (bool, optional): 是否查询类别。 Defaults to False.

    Raises:
        MiniggNotFoundError: 查询内容未找到。

    Returns:
        AnyDict | list[str]: 返回列表时，列表每一项元素都符合根据名称匹配的实际名称；返回字典则是此名称的实际数据。
    """
    params = {
        "query": query,
        "queryLanguages": query_languages.value,
        "resultLanguage": result_languages.value,
        **kwargs,
    }
    if match_categories:
        params["matchCategories"] = "1"
    async with AsyncClient(base_url=MINIGG_URL) as client:
        req = await client.get(endpoint, params=params)
        data = req.json()
        if req.status_code == 404:
            raise MiniggNotFoundError(**data)
        return data


async def get_weapon_info(
    name: str,
    query_languages: APILanguages = APILanguages.CHS,
    result_languages: APILanguages = APILanguages.CHS,
) -> Weapon | list[str]:
    """获取武器信息

    Args:
        name (str): 武器名称或类别名称。

        **其他参数另见 `minigg_request`。**

    Raises:
        MiniggNotFoundError: 武器未找到。

    Returns:
        Weapon | list[str]: 武器信息，如果为列表，则每个元素都是武器名。
            `get_weapon_costs` 和 `get_weapon_stats` 同
    """
    data = await minigg_request(
        "/weapons",
        name,
        query_languages=query_languages,
        result_languages=result_languages,
    )
    if isinstance(data, dict):
        data = cast(Weapon, data)
    return data


async def get_weapon_costs(
    name: str,
    query_languages: APILanguages = APILanguages.CHS,
    result_languages: APILanguages = APILanguages.CHS,
) -> WeaponCosts | list[str]:
    """获取武器信息（花费）

    Args:
        name (str): 武器名称或类别名称。

        **其他参数另见 `minigg_request`。**

    Raises:
        MiniggNotFoundError: 武器未找到。

    Returns:
        WeaponCosts | list[str]: 武器花费。
    """
    data = await minigg_request(
        "/weapons",
        name,
        query_languages=query_languages,
        result_languages=result_languages,
        costs=True,
    )
    if isinstance(data, dict):
        data = cast(WeaponCosts, data)
    return data


async def get_weapon_stats(
    name: str,
    stats: int,
    query_languages: APILanguages = APILanguages.CHS,
    result_languages: APILanguages = APILanguages.CHS,
) -> WeaponStats | list[str]:
    """_summary_

    Args:
        name (str): 武器名称或类别名称。
        stats (int): 查询指定武器在这个等级的基础面板。

        **其他参数另见 `minigg_request`。**

    Raises:
        MiniggNotFoundError: 武器未找到。
        ValueError: stats 大于 90 或小于等于 0。

    Returns:
        WeaponStats: 武器等级基础面板。
    """
    if stats > 90 or stats <= 0:
        raise ValueError("stats must <= 90 and > 0")

    data = await minigg_request(
        "/weapons",
        name,
        query_languages=query_languages,
        result_languages=result_languages,
        stats=stats,
    )
    if isinstance(data, dict):
        data = cast(WeaponStats, data)
    return data
